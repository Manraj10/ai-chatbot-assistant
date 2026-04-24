# AI Chatbot Assistant

A lightweight backend for session-based chat. The app keeps short conversation history per session, generates context-aware replies, and exposes a simple API that could later be connected to a real model provider.

## Overview

This project is less about the model itself and more about the backend shape around a chatbot:

- session creation
- rolling conversation memory
- transcript retrieval
- session cleanup

That makes it a useful starter for building a real chat product later.

## Built with

- Python
- FastAPI
- Pydantic

## What it does

- creates chat sessions with unique IDs
- stores recent user and assistant turns
- generates replies using recent conversation context
- lists active sessions
- deletes sessions when they are no longer needed

## API

### `POST /sessions`
Create a new chat session.

### `GET /sessions`
List active sessions with message counts and last-updated timestamps.

### `GET /sessions/{session_id}`
Fetch the transcript for one session.

### `POST /sessions/{session_id}/messages`
Send a user message and receive a reply.

### `DELETE /sessions/{session_id}`
Delete an existing session.

## Running locally

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Interactive docs:

```text
http://127.0.0.1:8000/docs
```

## Notes

The current reply engine is intentionally simple and local. The structure is set up so a real LLM provider could be added later without needing to redesign the session and message flow from scratch.
