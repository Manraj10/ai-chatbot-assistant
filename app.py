from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: str


class SessionResponse(BaseModel):
    session_id: str
    messages: list[ChatMessage]


def timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


sessions: dict[str, list[ChatMessage]] = defaultdict(list)


def generate_reply(history: list[ChatMessage], latest_user_message: str) -> str:
    recent_user_topics = [
        message.content for message in history if message.role == "user"
    ][-3:]
    context = " | ".join(recent_user_topics[:-1]) if len(recent_user_topics) > 1 else ""

    if context:
        return (
            "Here is a context-aware response based on your recent messages. "
            f"You have recently asked about: {context}. "
            f"For your latest request, start with this plan: {latest_user_message}"
        )

    return (
        "Here is a response to your request. "
        f"A good next step for this prompt is: {latest_user_message}"
    )


app = FastAPI(title="AI Chatbot Assistant", version="1.0.0")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "AI Chatbot Assistant is running"}


@app.post("/sessions")
def create_session() -> dict[str, str]:
    session_id = str(uuid4())
    sessions[session_id] = []
    return {"session_id": session_id}


@app.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str) -> SessionResponse:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(session_id=session_id, messages=sessions[session_id])


@app.post("/sessions/{session_id}/messages")
def send_message(session_id: str, payload: MessageRequest) -> dict[str, str]:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    user_message = ChatMessage(role="user", content=payload.content, created_at=timestamp())
    sessions[session_id].append(user_message)

    reply_text = generate_reply(sessions[session_id], payload.content)
    assistant_message = ChatMessage(
        role="assistant", content=reply_text, created_at=timestamp()
    )
    sessions[session_id].append(assistant_message)

    # Keep only the most recent 12 messages so memory stays lightweight.
    sessions[session_id] = sessions[session_id][-12:]

    return {"reply": reply_text, "session_id": session_id}
