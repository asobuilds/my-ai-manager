# Aso - AI Personal & Business Assistant

A multi-tenant AI assistant platform that connects Gmail, social accounts, job boards, health data, home management systems, and encrypted file storage into a single conversational interface. Users sign in, connect their accounts, and interact with an AI assistant (Agnes) that helps manage emails, track job applications, monitor inventory with carton/unit logic, schedule events, analyze health vitals, manage household assets, and store sensitive files — all through a premium dark-themed React dashboard.

## Features

- **AI Chat** — Conversational interface over all connected data via Agnes AI with tool calling support
- **Shop Manager** — Full inventory tracking with carton/units/dual-unit support, stock movements, low-stock alerts, reorder-level thresholds, and per-product discounts
- **Secure Encrypted Vault** — Client-side Fernet-encrypted file storage; files are encrypted before upload and can only be decrypted with the correct password
- **Data Inventory** — Ingest Gmail messages, prioritize by AI, generate draft replies, categorize by topic
- **Job Tracker** — Post jobs, ingest applications from LinkedIn/Indeed, Kanban-style pipeline tracking with scoring and categorization
- **Social Media** — Draft and schedule posts across platforms with AI generation and sentiment analysis
- **Calendar** — View and manage events with intelligent scheduling suggestions and color-coded event types
- **Health** — Log and track vitals (heart rate, blood pressure, weight, steps, calories) with trend charts and medical profile management
- **Home Management** — Catalog household assets, track warranties, schedule maintenance tasks with due-date reminders
- **Preferences** — Customizable themes (5 palettes), font sizes, dark/light/system mode toggle, per-user feature flags
- **Auth / RBAC** — JWT-based authentication with owner vs staff role separation; staff cannot access other owners' data
- **Proactive Intelligence** — Daily automated sales reports generated at 11 PM UTC using Pandas analytics on stock movement data

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19 · Next.js 16 · Tailwind CSS v4 · shadcn/ui · Framer Motion |
| Backend | Python 3.12 · FastAPI · SQLAlchemy ORM · SQLite (dev) / PostgreSQL (prod) |
| AI | Agnes AI (OpenCode-powered conversational engine) |
| Auth | Passlib bcrypt · python-jose JWT · OAuth2 password flow |
| Security | Fernet encryption (cryptography library) for vault file storage |
| Analytics | Pandas for daily sales reports and shop analytics |
| Scheduler | APScheduler for background daily report generation |
| Integrations | Google APIs (Gmail, Calendar), RSS feed parsing, mock external services |

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- `pip`, `npm` or `yarn`

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
pytest                          # run all tests
```

### Frontend
```bash
cd frontend-react
npm install
npm run build                   # verify production build
npm start                       # dev server on port 3000
```

### Full Setup (Backend + Frontend together)
```bash
# From repo root
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=backend pytest -q    # run backend tests (131 tests)
cd frontend-react && npm install && npm run build
```

## Screenshots

See `docs/screenshots/` for placeholder images of:
- Landing page (dark slate hero with glassmorphism nav)
- Dashboard overview (KPI cards, quick actions toolbar)
- Data Inventory inbox view
- Shop Manager product table with carton/unit display
- Health vitals chart
- Job application Kanban pipeline
- Secure Vault file browser
- Login / signup pages

---

Built with [OpenCode](https://opencode.ai) and powered by Agnes AI.
