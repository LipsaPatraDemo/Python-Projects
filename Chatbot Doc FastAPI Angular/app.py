from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4

from chatbot import interpret_message

app = FastAPI(title="Doctor Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conversations = {}


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


@app.post("/chat")
def chat(payload: ChatRequest):
    if not payload.message or not payload.message.strip():
        raise HTTPException(status_code=400, detail="The 'message' field is required.")

    conversation_id = payload.conversation_id or str(uuid4())
    conversation = conversations.setdefault(conversation_id, [])

    try:
        reply = interpret_message(payload.message, conversation)
        return {
            "conversation_id": conversation_id,
            "reply": reply,
        }
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def home():
    return {"message": "Doctor Chatbot API is running"}
