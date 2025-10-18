
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx, os

API_BASE = os.getenv("API_URL", "http://localhost:8000")
app = FastAPI()
templates = Jinja2Templates(directory="webui/templates")
app.mount("/static", StaticFiles(directory="webui/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "answer": None, "citations": [], "question": ""})

@app.post("/ask", response_class=HTMLResponse)
def ask(request: Request, question: str = Form(...), k: int = Form(5), temperature: float = Form(0.0)):
    payload = {"question": question, "k": int(k), "temperature": float(temperature)}
    try:
        r = httpx.post(f"{API_BASE}/ask", json=payload, timeout=60)
        r.raise_for_status()
        j = r.json()
        answer = j.get("answer", "")
        citations = j.get("citations", [])
    except Exception as e:
        answer = f"Error contacting RAG API: {str(e)}"
        citations = []
    return templates.TemplateResponse("index.html", {"request": request, "answer": answer, "citations": citations, "question": question})
