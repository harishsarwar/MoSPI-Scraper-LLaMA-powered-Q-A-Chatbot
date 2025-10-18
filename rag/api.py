
from fastapi import FastAPI
from pydantic import BaseModel
import os
from rag.retriever import Retriever
from rag.prompt_groq import build_prompt, call_groq
from loguru import logger

app = FastAPI()
DB_DIR = os.getenv("PROCESSED_DIR","./data/processed")
retriever = Retriever(db_dir=DB_DIR)

class AskRequest(BaseModel):
    question: str
    k: int = None
    temperature: float = 0.0

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/ingest")
def ingest():
    retriever.rebuild_index()
    return {"status":"index_rebuilt"}

@app.post("/ask")
def ask(req: AskRequest):
    k = req.k or int(os.getenv("K_RETRIEVE","5"))
    hits = retriever.retrieve(req.question, k=k)
    context = "\n\n".join([f"TITLE: {h['title']}\nURL: {h['source']}\n\n{h['text']}" for h in hits])
    messages = build_prompt(context, req.question)
    response = call_groq(messages, temperature=req.temperature)
    citations = []
    seen = set()
    for h in hits:
        if h['source'] not in seen:
            citations.append({"title": h['title'], "url": h['source']})
            seen.add(h['source'])
    return {"answer": response, "citations": citations}
