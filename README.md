# AI Chatbot Assistant

A session-based chat app built with FastAPI. It includes a browser UI, multiple response modes, rolling conversation memory, and a backend structure that can later be wired up to a real model provider.

## Overview

This project focuses on the application layer around chat:

- session management
- conversation history
- provider-style response behavior
- browser interaction on top of an API backend

The current response engine is local and deterministic, but the session flow is built to make a real model integration straightforward later.

## Built with

- Python
- FastAPI
- Pydantic
- HTML
- JavaScript

## Features

- create chat sessions with different response modes
- switch between `planner`, `coach`, and `explainer` behavior
- keep rolling memory for recent turns
- list and revisit active sessions
- delete sessions when they are no longer needed
- use a lightweight browser UI on top of the API

## API

### `GET /api/providers`
List available response modes.

### `POST /api/sessions`
Create a new session with a provider.

### `GET /api/sessions`
List current sessions.

### `GET /api/sessions/{session_id}`
Fetch one session and its transcript.

### `POST /api/sessions/{session_id}/messages`
Send a user message and receive a response.

### `DELETE /api/sessions/{session_id}`
Delete a session.

## Running locally

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Open the app:

```text
http://127.0.0.1:8000/
```

Interactive docs:

```text
http://127.0.0.1:8000/docs
```

## Notes

The provider abstraction in this version is intentionally lightweight. It is there to model how different assistant behaviors can sit behind the same session and message flow before connecting to a hosted LLM.
