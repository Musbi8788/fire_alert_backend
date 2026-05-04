# FireAlert Backend

FastAPI backend for FireAlert GM. Exposes REST endpoints under `/api/*`.

---

## Requirements

- Python 3.11+
- uv (https://github.com/astral-sh/uv)

---

## Setup

Create a `.env` file from `.env.example`:

```env
DATABASE_URL=sqlite:///./firealert.db
JWT_SECRET=your-secret-key
PORT=8080
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me
ADMIN_FULLNAME=Admin User
```

Install deps and create tables:

```bash
uv sync
uv run python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"
```

---

## Run

```bash
uv run uvicorn main:app --reload --host localhost --port 8080
```

---

## Project Layout

```
+-- app/            # routers, models, auth, db
+-- main.py         # FastAPI entrypoint
+-- pyproject.toml  # Python package/dependencies
+-- render.yaml     # Render deploy blueprint
```

---

## Deploy To Render

Use this folder as the GitHub repo root.

`render.yaml` configures:

- Build Command: `pip install .`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Python version: `3.12`

Set these Render environment variables:

```env
DATABASE_URL=postgresql://...
FRONTEND_ORIGINS=https://your-frontend.vercel.app
ADMIN_PASSWORD=change-me
```

Render can generate `JWT_SECRET` from the blueprint. Use hosted PostgreSQL for production, not the local SQLite file.

---

## Notes

- There are no migrations yet; tables are created with `Base.metadata.create_all`.
- Default admin seed values are read from `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_FULLNAME` if set.
