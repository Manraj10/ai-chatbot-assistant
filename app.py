from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4
import re

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


SessionCreateRequest.model_rebuild()
SessionState.model_rebuild()
SessionListItem.model_rebuild()


def timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")


sessions: dict[str, SessionState] = {}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def detect_topic(message: str) -> str:
    text = normalize(message)
    if "ap gov" in text or "government" in text or "gov" in text:
        return "ap_gov"
    if "resume" in text or "job" in text or "internship" in text:
        return "career"
    if "study" in text or "exam" in text or "test" in text:
        return "study"
    if "project" in text or "code" in text or "app" in text:
        return "build"
    return "general"


def planner_reply(history: list[ChatMessage], latest_user_message: str) -> str:
    topic = detect_topic(latest_user_message)
    if topic == "ap_gov":
        return (
            "Here is a simple AP Gov study plan you can use tonight:\n\n"
            "1. Spend 20 minutes reviewing foundational documents and what each one did.\n"
            "2. Spend 20 minutes on core concepts like federalism, separation of powers, and checks and balances.\n"
            "3. Spend 15 minutes reviewing Supreme Court cases and why they matter.\n"
            "4. Spend 15 minutes doing practice multiple choice or FRQs.\n"
            "5. End by writing a one-page cheat sheet from memory.\n\n"
            "If you want, I can turn that into a 3-day AP Gov cram plan."
        )
    if topic == "career":
        return (
            "Here is a practical plan:\n\n"
            "1. Pick one target role.\n"
            "2. Match your resume bullets to that role.\n"
            "3. Surface 2-3 strongest projects.\n"
            "4. Prepare a short answer for why you want the role.\n"
            "5. Submit, then track follow-ups in one list.\n\n"
            "If you want, I can turn this into a same-day internship application checklist."
        )
    if topic == "build":
        return (
            "Start with this build order:\n\n"
            "1. Define the smallest useful version of the app.\n"
            "2. Set up the data model and API routes.\n"
            "3. Build the UI around one working flow.\n"
            "4. Test one real user path end to end.\n"
            "5. Polish the README and deployment instructions.\n\n"
            "If you want, I can help break your idea into backend, frontend, and deployment tasks."
        )
    return (
        "Here is a clean next-step plan:\n\n"
        "1. Clarify the goal.\n"
        "2. Break it into 3 small actions.\n"
        "3. Do the highest-value action first.\n"
        "4. Check what changed.\n"
        "5. Adjust from there.\n\n"
        "If you want, I can make that plan specific to your exact situation."
    )


def coach_reply(history: list[ChatMessage], latest_user_message: str) -> str:
    topic = detect_topic(latest_user_message)
    if topic in {"study", "ap_gov"}:
        return (
            "You do not need to master everything at once.\n\n"
            "Focus on one unit, one concept list, and one practice set at a time. "
            "If you stay consistent for even 45 focused minutes, that is enough to make progress tonight.\n\n"
            "Tell me what unit you are stuck on and I will help you simplify it."
        )
    if topic == "career":
        return (
            "You are already in a stronger position than you think.\n\n"
            "You have a real internship, a strong school brand, and actual projects. "
            "The goal now is not to look perfect, it is to look credible and apply fast.\n\n"
            "Send me the role you want and I will help you tailor for it."
        )
    return (
        "The best move is to keep this simple and get one real win first.\n\n"
        "Pick the next concrete step, finish it, and then improve from there. "
        "Momentum matters more than making it perfect on the first try."
    )


def explainer_reply(history: list[ChatMessage], latest_user_message: str) -> str:
    topic = detect_topic(latest_user_message)
    if topic == "ap_gov":
        return (
            "AP Gov is mostly about understanding how power is structured and limited in the U.S. system.\n\n"
            "The big ideas are:\n"
            "- constitutional foundations\n"
            "- federalism\n"
            "- branches of government\n"
            "- civil liberties and civil rights\n"
            "- political participation and public policy\n\n"
            "A good way to study is to connect each topic to one example, one court case, and one real effect.\n\n"
            "If you want, I can explain AP Gov unit by unit in a way that is easier to memorize."
        )
    if topic == "career":
        return (
            "For internships, recruiters usually scan for three things first:\n\n"
            "- proof you can build or contribute\n"
            "- proof you can learn quickly\n"
            "- proof you can communicate clearly\n\n"
            "That is why your internship, coursework, and projects matter more than trying to sound overly advanced.\n\n"
            "If you want, I can explain how to position your background for software engineering roles specifically."
        )
    if topic == "build":
        return (
            "A strong software project usually has four parts:\n\n"
            "- a clear problem\n"
            "- a working implementation\n"
            "- technical decisions you can explain\n"
            "- a polished README and demo path\n\n"
            "The project becomes stronger when the app solves a real flow instead of just showing disconnected features."
        )
    return (
        "A good explanation should do three things:\n\n"
        "- define the idea clearly\n"
        "- break it into smaller parts\n"
        "- connect it to a concrete example\n\n"
        "If you want, give me the topic and I will explain it in that format."
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
