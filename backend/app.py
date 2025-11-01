import os, json, math
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY must be set")

openai.api_key = OPENAI_API_KEY

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "embeddings.json")
with open(DATA_FILE, "r", encoding="utf-8") as f:
    EMBEDS = json.load(f)

def cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    if na == 0 or nb == 0: return 0.0
    return dot/(na*nb)

app = FastAPI(title="Perplexity MVP - Render")

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class QueryReq(BaseModel):
    query: str
    top_k: int = 4

@app.post("/qa")
async def qa(req: QueryReq):
    q = req.query
    emb_resp = openai.Embedding.create(input=[q], model="text-embedding-3-small")
    q_emb = emb_resp["data"][0]["embedding"]

    scored = []
    for item in EMBEDS:
        s = cosine(q_emb, item["embedding"])
        scored.append((s, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [x[1] for x in scored[:req.top_k]]

    context = "\n\n---\n\n".join([f"Title: {t['title']}\nURL: {t['url']}\nText: {t['text']}" for t in top])
    system = ("You are an answer engine. Use ONLY the sources below to answer. "
              "Return a concise answer (2-4 sentences) and then a numbered list of sources as Title — URL.")
    user = f"QUESTION: {q}\n\nSOURCES:\n{context}"

    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system","content":system}, {"role":"user","content":user}],
        max_tokens=300,
        temperature=0.0
    )
    answer = chat["choices"][0]["message"]["content"]
    return {"answer": answer, "sources": top}

@app.post("/chat")
async def chat(req: QueryReq):
    return await qa(req)

