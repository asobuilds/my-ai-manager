# AGENTS.md

## Project Overview
Python-based multi-tenant AI assistant platform. Backend in `backend/`, integrations (Gmail, job boards, files) in `backend/app/integrations/`, tests in `tests/`.

## Setup
- Create venv: `python -m venv .venv`
- Activate (Windows): `.venv\Scripts\activate`
- Activate (macOS/Linux): `source .venv/bin/activate`
- Install deps: `pip install -r requirements.txt`

## Dev Commands
- Run tests: `pytest`
- Lint: `ruff check .` 

## Code Style
- Python 3.11+
- Type hints on all public functions
- Format with `black`

## Guardrails
- Never commit `.env` files or API keys
- Never auto-send emails or auto-submit job applications without explicit user approval
- All user data access must be scoped by `user_id`
- Any tool that writes/deletes must require a `confirm=True` flag

## Testing
- Every new tool function needs a test in `tests/`
- Run `pytest` before reporting a task complete
