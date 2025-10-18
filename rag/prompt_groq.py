
import os, httpx, json

GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

SYSTEM_PROMPT = (
    "You are an assistant that answers strictly from the provided context. "
    "If the answer cannot be found in the context, reply exactly: 'I don't have that in my data.' "
    "When you include information from the context, include bullet citations with title and URL."
)

def build_prompt(context, question):
    user_content = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

def call_groq(messages, temperature=0.0, max_tokens=512):
    if not GROQ_API_KEY:
        return "I don't have that in my data."
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": float(temperature),
        "max_output_tokens": int(max_tokens)
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    with httpx.Client(timeout=60) as client:
        r = client.post(GROQ_API_URL, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
        if "choices" in data and len(data["choices"])>0:
            return data["choices"][0].get("message",{}).get("content","")
        if "response" in data:
            return data["response"].get("output", "")
        return json.dumps(data)
