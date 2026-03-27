# Who Said That?!

A darkly absurd quote-guessing game. Five rounds, two choices, zero excuses.
Built with FastAPI + SQLite (backend) and Flet (desktop frontend).

---

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager

---

## Setup

**1. Install dependencies**
```bash
uv sync
```

**2. Create your environment file**
```bash
cp .env.example .env
```
Then open `.env` and set `SECRET_KEY` to a random string:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Architecture

The app follows a client-server architecture with a clear separation between backend and frontend, both running locally as separate processes.

```
┌─────────────────────┐        HTTP/JSON        ┌──────────────────────┐
│   Flet Frontend     │  ──────────────────────▶ │   FastAPI Backend    │
│   (desktop app)     │ ◀──────────────────────  │   (localhost:8000)   │
└─────────────────────┘                          └──────────┬───────────┘
                                                            │ SQLAlchemy async
                                                            ▼
                                                 ┌──────────────────────┐
                                                 │   SQLite Database    │
                                                 │   who_said_that.db   │
                                                 └──────────────────────┘
```

### Backend — `src/backend/`
| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async) |
| Database | SQLite via aiosqlite |
| Auth | JWT tokens (python-jose) + bcrypt password hashing |
| Settings | pydantic-settings (reads from `.env`) |
| Server | Uvicorn |

Three REST routers: `auth` (register/login), `game` (start session, submit answers), `leaderboard`.

**Data model**: `User` → `GameSession` → `GameRound` (links a `Quote` to a correct `Person` and a wrong `Person`). Each round stores the user's answer and whether it was correct.

### Frontend — `src/frontend/`
| Layer | Technology |
|---|---|
| UI framework | Flet 0.82 (Flutter-based) |
| HTTP client | httpx |

Five views: `login`, `home`, `game`, `result`, `leaderboard`. State is held in a single `AppState` object passed through the navigator. The `APIClient` wraps all backend calls.

### Static image serving
On first run, the backend downloads all character portraits from Wikimedia (server-side, with rate-limit handling) and saves them to `static/images/`. FastAPI serves this directory at `/static`. Images are stored locally so the app works offline after the first run.

---

## Running the app

### Together (recommended)
Starts backend and frontend in a single command. Close the window to shut both down.
```bash
uv run python run.py
```

### Separately

**Backend only** (API on http://localhost:8000)
```bash
uv run uvicorn backend.main:app --reload --port 8000
```

**Frontend only** (assumes backend is already running)
```bash
uv run python -m frontend.main
```

---

## First run

On first startup the backend seeds the database and downloads all character images (~2 minutes).
Subsequent startups are instant — images are cached locally in `static/images/`.

---

## Project structure

```
src/
  backend/    FastAPI app, models, routes, seed data
  frontend/   Flet desktop app, views, theme
static/       Downloaded character images (auto-generated, not committed)
run.py        Launches backend + frontend together
.env          Your local environment variables (not committed)
.env.example  Template for .env
```
