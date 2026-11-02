# AI Personal Management Assistant

A multi-tenant AI assistant platform that connects Gmail, social accounts, and job boards to help users manage email, automate responses, track applications, and organize files.

## Vision
Build a consumer product where anyone can sign in, connect their accounts, and have a conversational AI assistant that handles the busywork.

## Core Features (Planned)
- Gmail filtering, categorization, and draft/auto responses
- Job application automation and tracking
- File cataloging and retrieval
- Conversational interface over all connected data

## Tech Stack
- Python 3.11+ (FastAPI backend)
- SQLAlchemy (SQLite for dev, PostgreSQL for prod)
- OpenCode + Agnes AI (development agent)
- Google APIs (Gmail, Calendar)

## Getting Started (Local Development)
1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run tests: `pytest`
