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
- The Secure Vault uses **Fernet encryption** — files are encrypted client-side with the user's password before being stored; raw bytes never hit the database.
- The Shop module stores `stock_quantity` in **base units internally**; cartons are converted on input (`quantity × units_per_carton`). Stock movements record both the original unit entry and the base-unit equivalent for auditing.
- Before committing, ensure `PYTHONPATH=backend pytest -q` passes and `npm run build` succeeds in `frontend-react/`.

## Tech Stack
- **Frontend:** React 19 · Next.js 16 · Tailwind CSS v4 · shadcn/ui · Framer Motion
- **Backend:** Python 3.12 · FastAPI · SQLAlchemy ORM · SQLite (dev) / PostgreSQL (prod)
- **AI:** Agnes AI (conversational engine)
- **Auth:** Passlib bcrypt · python-jose JWT · OAuth2 password flow
- **Security:** `cryptography` library (Fernet symmetric encryption for vault)
- **Analytics:** Pandas (daily sales reports and shop analytics)
- **Scheduler:** APScheduler (background cron jobs)
- **Integrations:** Google APIs (Gmail, Calendar), RSS parsers, mock external services

## Key Modules

### Backend (`backend/app/api/`)
| Module | Description |
|--------|-------------|
| `auth.py` | Login, register, token issuance, logout |
| `chat.py` | Agnes AI chat endpoint with system prompt injection and calendar tool |
| `messages.py` | Gmail ingestion, prioritization, draft generation |
| `shop.py` | Products, stock movements (carton/piece conversion), low-stock alerts, daily sales analytics |
| `jobs.py` | Job postings, application ingestion, scoring |
| `social.py` | Social post drafts, scheduling, sentiment tags |
| `calendar.py` | Event CRUD, sync endpoints |
| `health.py` | Health profile, vitals logging, trend endpoints |
| `home.py` | Home assets, maintenance tasks, due-date tracking |
| `vault.py` | Encrypted file upload/download, password-gated decryption |
| `preferences.py` | Theme, font size, enabled features per user (auto-enforces all feature flags) |

### Backend Services (`backend/app/services/`)
| Module | Description |
|--------|-------------|
| `scheduler.py` | APScheduler `BackgroundScheduler` — runs `generate_daily_report()` for all users at 23:00 UTC |
| `analytics.py` | Pandas-powered daily sales report generator and weekly analytics summary |
| `ingestion.py` | Email/feed ingestion logic |
| `priority_engine.py` | Message prioritization scoring |
| `social_generator.py` | AI post content generation |

### Frontend (`frontend-react/src/`)
| Directory | Description |
|-----------|-------------|
| `app/dashboard/*` | Dashboard sub-pages: chat, inventory, shop, jobs, social, calendar, health, home, settings, profile, vault |
| `components/landing/*` | Landing page sections: hero, capabilities, testimonials, FAQ, footer |
| `contexts/*` | PreferenceContext, theme context providers |
| `lib/api.ts` | Axios instance with JWT interceptor, 401 unauth event dispatch |

## Testing
- Backend: `PYTHONPATH=backend .venv/bin/python -m pytest -q`
  - Test suite: **131 tests** covering auth, shop, chat, calendar, social, jobs, preferences, health, home, vault, proactive intelligence, and RBAC.
- Frontend: `npm run build` (in `frontend-react/`)
- Every new tool function needs a test in `tests/`
- Lint: `npx eslint <files>` (ruff not installed)
