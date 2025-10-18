
import os, json
import faiss, numpy as np
from sentence_transformers import SentenceTransformer

class Retriever:
    def __init__(self, db_dir="./data/processed", embed_model=None):
        self.db_dir = db_dir
        self.embed_model = embed_model or os.getenv("EMBEDDING_MODEL","sentence-transformers/all-MiniLM-L6-v2")
        self.model = SentenceTransformer(self.embed_model)
        idx_path = os.path.join(db_dir,"faiss.index")
        if os.path.exists(idx_path):
            self.index = faiss.read_index(idx_path)
            self.metadatas = json.load(open(os.path.join(db_dir,"metadatas.json"),'r', encoding='utf-8'))
        else:
            self.index = None
            self.metadatas = []

    def rebuild_index(self):
        from pipeline.run import build_index, load_documents
        docs = load_documents()
        build_index(docs)
        self.__init__(db_dir=self.db_dir, embed_model=self.embed_model)

    def retrieve(self, query, k=5):
        if self.index is None:
            return []
        qvec = self.model.encode(query).astype('float32')
        D, I = self.index.search(np.expand_dims(qvec, axis=0), k)
        results = []
        for idx in I[0]:
            if idx < 0 or idx >= len(self.metadatas):
                continue
            md = self.metadatas[idx]
            results.append(md)
        return results
