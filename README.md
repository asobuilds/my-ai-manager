# Aso - AI Personal & Business Assistant

A multi-tenant AI assistant platform that connects Gmail, social accounts, job boards, health data, and home management systems into a single conversational interface. Users sign in, connect their accounts, and interact with an AI assistant (Agnes) that helps manage emails, track job applications, monitor inventory, schedule events, analyze health vitals, and automate business workflows — all through a premium dark-themed React dashboard.

## Features

- **AI Chat** — Conversational interface over all connected data via Agnes AI
- **Shop Manager** — Track products, stock levels, reorder alerts, and supplier info
- **Data Inventory** — Ingest Gmail messages, prioritize by AI, generate draft replies
- **Job Tracker** — Post jobs, ingest applications from LinkedIn/Indeed, categorize and score leads
- **Social Media** — Draft and schedule posts across platforms with sentiment analysis
- **Calendar** — View and manage events with intelligent scheduling suggestions
- **Health** — Log and track vitals (heart rate, blood pressure, weight, etc.) with trend charts
- **Home Management** — Catalog assets and maintenance tasks for property management
- **Preferences** — Customizable themes, font sizes, and feature toggles per user
- **Auth / RBAC** — JWT-based authentication with owner vs staff role separation; staff cannot access other owners' data

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19 · Next.js 16 · Tailwind CSS v4 · shadcn/ui · Framer Motion |
| Backend | Python 3.12 · FastAPI · SQLAlchemy · SQLite (dev) / PostgreSQL (prod) |
| AI | Agnes AI (OpenCode-powered conversational engine) |
| Auth | Passlib bcrypt · python-jose JWT · OAuth2 password flow |
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
PYTHONPATH=backend pytest -q    # run backend tests
cd frontend-react && npm install && npm run build
```

## Screenshots

See `docs/screenshots/` for placeholder images of:
- Landing page (dark slate hero with glassmorphism nav)
- Dashboard overview (KPI cards, quick actions toolbar)
- Data Inventory inbox view
- Shop Manager product table
- Health vitals chart
- Job application pipeline
- Login / signup pages

---

Built with [OpenCode](https://opencode.ai) and powered by Agnes AI.
