# (انسخ هذا الملف بالكامل)

import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic

# =================
# Config
# =================
API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not API_KEY:
    raise RuntimeError("Missing API Key")

client = anthropic.Anthropic(api_key=API_KEY)

app = FastAPI(title="Said AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS = {}

# =================
# Models
# =================

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


# =================
# Routes
# =================

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    history = SESSIONS.get(session_id, [])
    history.append({"role": "user", "content": req.message})

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1024,
            messages=history
        )

        reply = response.content[0].text

    except Exception as e:
        raise HTTPException(500, str(e))

    history.append({"role": "assistant", "content": reply})
    SESSIONS[session_id] = history

    return {
        "session_id": session_id,
        "reply": reply
    }
