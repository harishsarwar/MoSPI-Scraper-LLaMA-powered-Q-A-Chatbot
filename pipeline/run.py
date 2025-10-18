
import os, json
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from scraper.utils import write_json, read_json, structured_log

DB_DIR = os.getenv("PROCESSED_DIR","./data/processed")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL","sentence-transformers/all-MiniLM-L6-v2")

def load_documents():
    p = os.path.join(DB_DIR,"documents.json")
    if not os.path.exists(p):
        structured_log("documents_missing", path=p)
        return []
    return read_json(p) or []

def chunk_text(text, approx_chars=3000):
    if not text:
        return []
    max_size = approx_chars
    overlap = int(max_size * 0.1)
    chunks = []
    start = 0
    L = len(text)
    while start < L:
        end = min(start + max_size, L)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == L:
            break
        start = end - overlap
    return chunks

def build_index(docs):
    model = SentenceTransformer(EMBED_MODEL)
    embeddings = []
    metadatas = []
    for d in docs:
        doc_id = d['id']
        for f in d.get('files',[]):
            text = f.get('text','') or ''
            if not text:
                continue
            chunks = chunk_text(text)
            for i,c in enumerate(chunks):
                emb = model.encode(c)
                embeddings.append(emb)
                metadatas.append({"doc_id": doc_id, "chunk_id": f"{doc_id}_{i}", "text": c, "source": d['url'], "title": d['title']})
    if not embeddings:
        structured_log("no_embeddings")
        return
    X = np.vstack(embeddings).astype('float32')
    d = X.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(X)
    faiss.write_index(index, os.path.join(DB_DIR,"faiss.index"))
    write_json(os.path.join(DB_DIR,"metadatas.json"), metadatas)
    write_json(os.path.join(DB_DIR,"catalog.json"), {"n_docs": len(docs), "n_chunks": X.shape[0]})
    structured_log("index_built", n=X.shape[0])

if __name__ == "__main__":
    docs = load_documents()
    build_index(docs)
