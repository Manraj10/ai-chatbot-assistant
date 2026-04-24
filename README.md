# AI Chatbot Assistant

A session-aware backend for a conversational assistant that keeps track of recent messages, builds responses from prior context, and exposes a clean API for multi-turn chat. This project is intentionally structured to show backend architecture and conversation-state handling in a way that can later plug into a real model provider.

## Why this project is strong

This project demonstrates:

- stateful backend design
- session memory management
- prompt assembly and response generation flow
- API structure that can later connect to a production AI provider

## Tech stack

- Python
- FastAPI
- Pydantic

## Features

- create chat sessions
- send multi-turn user messages
- keep rolling memory of recent conversation turns
- generate contextual responses based on the session history
- inspect a session transcript

## Run locally

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Resume-ready description

Built a FastAPI-based conversational assistant with session memory and structured response generation, supporting multi-turn chat behavior, message history management, and extensible backend design for future AI model integration.
