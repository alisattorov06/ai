import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from gemini_pool import GeminiPool

load_dotenv()

keys = [k.strip() for k in os.getenv("GEMINI_KEYS", "").split(",") if k.strip()]
gemini = GeminiPool(keys)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

chat_history = []

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        reply = gemini.generate(req.message)
    except RuntimeError as e:
        reply = str(e)

    chat_history.append({"role": "user", "text": req.message})
    chat_history.append({"role": "ai", "text": reply})
    return {"reply": reply}

@app.get("/history")
def history():
    return chat_history
