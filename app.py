from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).parent
INDEX_HTML = BASE_DIR / "index.html"

ProviderName = Literal["planner", "coach", "explainer"]


class MessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class SessionCreateRequest(BaseModel):
    provider: ProviderName = "planner"


class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: str


class SessionState(BaseModel):
    session_id: str
    provider: ProviderName
    created_at: str
    messages: list[ChatMessage]


class SessionListItem(BaseModel):
    session_id: str
    provider: ProviderName
    total_messages: int
    last_updated: str | None


def timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


sessions: dict[str, SessionState] = {}


def planner_reply(history: list[ChatMessage], latest_user_message: str) -> str:
    context = [message.content for message in history if message.role == "user"][-2:]
    summary = f" Recent context: {' | '.join(context[:-1])}." if len(context) > 1 else ""
    return (
        "Plan mode: break the request into the smallest useful next actions."
        f"{summary} Start here: {latest_user_message}"
    )


def coach_reply(history: list[ChatMessage], latest_user_message: str) -> str:
    turns = len([message for message in history if message.role == "user"])
    return (
        "Coach mode: keep the response practical and encouraging. "
        f"This is turn {turns}. Focus on progress and clarity for: {latest_user_message}"
    )


def explainer_reply(history: list[ChatMessage], latest_user_message: str) -> str:
    prior_topics = [message.content for message in history if message.role == "user"][-2:]
    references = f" Earlier topics: {' | '.join(prior_topics[:-1])}." if len(prior_topics) > 1 else ""
    return (
        "Explainer mode: answer with structure, examples, and reasoning."
        f"{references} Topic to explain: {latest_user_message}"
    )


PROVIDERS = {
    "planner": planner_reply,
    "coach": coach_reply,
    "explainer": explainer_reply,
}


app = FastAPI(title="AI Chatbot Assistant", version="2.0.0")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return INDEX_HTML.read_text(encoding="utf-8")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/providers")
def list_providers() -> dict[str, list[str]]:
    return {"providers": list(PROVIDERS)}


@app.post("/api/sessions", response_model=SessionState)
def create_session(payload: SessionCreateRequest) -> SessionState:
    session = SessionState(
        session_id=str(uuid4()),
        provider=payload.provider,
        created_at=timestamp(),
        messages=[],
    )
    sessions[session.session_id] = session
    return session


@app.get("/api/sessions", response_model=list[SessionListItem])
def list_sessions() -> list[SessionListItem]:
    items: list[SessionListItem] = []
    for session in sessions.values():
        items.append(
            SessionListItem(
                session_id=session.session_id,
                provider=session.provider,
                total_messages=len(session.messages),
                last_updated=session.messages[-1].created_at if session.messages else session.created_at,
            )
        )
    return items


@app.get("/api/sessions/{session_id}", response_model=SessionState)
def get_session(session_id: str) -> SessionState:
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.post("/api/sessions/{session_id}/messages")
def send_message(session_id: str, payload: MessageRequest) -> dict[str, str]:
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_message = ChatMessage(role="user", content=payload.content, created_at=timestamp())
    session.messages.append(user_message)

    reply_text = PROVIDERS[session.provider](session.messages, payload.content)
    assistant_message = ChatMessage(role="assistant", content=reply_text, created_at=timestamp())
    session.messages.append(assistant_message)
    session.messages = session.messages[-14:]

    return {"reply": reply_text, "session_id": session_id, "provider": session.provider}


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str) -> dict[str, str]:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    del sessions[session_id]
    return {"message": "Session deleted", "session_id": session_id}
