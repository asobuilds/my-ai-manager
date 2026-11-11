# AGENTS.md

## Project Overview
Python-based multi-tenant AI assistant platform. Backend in `backend/`, integrations (Gmail, job boards, files) in `backend/app/integrations/`, tests in `tests/`.

## Core Rules
- Run `pytest` before finishing any backend task; run `npm run build` before finishing any frontend task.
- Never commit `.env` files or API keys.
- Never auto-send emails or auto-submit job applications without explicit user approval (human-in-the-loop).
- All user data access must be scoped by `user_id`.
- Any tool that writes/deletes must require a `confirm=True` flag.
- Respect RBAC: only `owner` users can modify shared resources; `staff` is read-only within their assigned owner's scope.

## Tech Stack
- **Frontend:** React 19 · Next.js 16 · Tailwind CSS v4 · shadcn/ui · Framer Motion
- **Backend:** Python 3.12 · FastAPI · SQLAlchemy ORM · SQLite (dev) / PostgreSQL (prod)
- **AI:** Agnes AI (conversational engine)
- **Auth:** Passlib bcrypt · python-jose JWT · OAuth2 password flow
- **Integrations:** Google APIs (Gmail, Calendar), RSS parsers, mock external services

## Key Modules

### Backend (`backend/app/api/`)
| Module | Description |
|--------|-------------|
| `auth.py` | Login, register, token issuance, logout |
| `chat.py` | Agnes AI chat endpoint with system prompt injection |
| `messages.py` | Gmail ingestion, prioritization, draft generation |
| `shop.py` | Products, stock movements, low-stock alerts |
| `jobs.py` | Job postings, application ingestion, scoring |
| `social.py` | Social post drafts, scheduling, sentiment tags |
| `calendar.py` | Event CRUD, sync endpoints |
| `health.py` | Health profile, vitals logging, trend endpoints |
| `home.py` | Home assets, maintenance tasks, due-date tracking |
| `preferences.py` | Theme, font size, enabled features per user |

### Frontend (`frontend-react/src/`)
| Directory | Description |
|-----------|-------------|
| `app/dashboard/*` | Dashboard sub-pages: chat, inventory, shop, jobs, social, calendar, health, home, settings, profile |
| `components/landing/*` | Landing page sections: hero, capabilities, testimonials, FAQ, footer |
| `contexts/*` | PreferenceContext, theme context providers |
| `lib/api.ts` | Axios instance with JWT interceptor, 401 unauth event dispatch |

## Testing
- Backend: `PYTHONPATH=backend .venv/bin/python -m pytest -q`
- Frontend: `npm run build` (in `frontend-react/`)
- Every new tool function needs a test in `tests/`
- Lint: `npx eslint <files>` (ruff not installed)
