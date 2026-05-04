# Fire Alert Backend

Production-ready FastAPI backend for the Fire Alert emergency reporting platform. The API powers user registration, login, fire incident reporting, admin incident management, map data, and dashboard statistics.

The production backend is intended to run on **Railway**, while the frontend is deployed on **Vercel**.

Live frontend demo: https://fire-alert-mu.vercel.app/

Production API: https://fire-alert-backend-production.up.railway.app/

## System Overview

Fire Alert connects citizens with emergency response teams by collecting structured fire reports with GPS coordinates and making them available to administrators in a command-center dashboard.

Core backend responsibilities:

- User registration and JWT-based authentication.
- Fire report creation with description, latitude, longitude, and optional address.
- User report history.
- Admin-only incident feed with status filtering.
- Admin report status updates: `pending`, `in-progress`, and `resolved`.
- Admin dashboard statistics.
- Health check endpoint for hosting platforms.
- Automatic database table creation on application startup.
- Admin user seeding from environment variables.

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL for production
- SQLite for local development
- JWT authentication with `python-jose`
- Password hashing with `passlib`
- Uvicorn ASGI server

## API Surface

All API routes are mounted under `/api`.

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/healthz` | Health check |
| `POST` | `/api/users/register` | Register a user |
| `POST` | `/api/users/login` | Login and receive a JWT |
| `POST` | `/api/reports` | Submit a fire report |
| `GET` | `/api/reports` | Get the authenticated user's reports |
| `GET` | `/api/admin/reports` | Get all reports, optionally filtered by status |
| `PATCH` | `/api/admin/reports/{report_id}/status` | Update a report status |
| `GET` | `/api/admin/stats` | Get admin dashboard totals |

Interactive API documentation is available at `/docs` when the backend is running.

## Requirements

- Python 3.11 or newer
- `uv` package manager: https://github.com/astral-sh/uv
- PostgreSQL database for production deployments

## Local Setup

Create a local environment file:

```bash
cp .env.example .env
```

Example local `.env`:

```env
DATABASE_URL=sqlite:///./firealert.db
JWT_SECRET=change-me
PORT=8080
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me
ADMIN_FULLNAME=Admin User
```

Install dependencies:

```bash
uv sync
```

Start the API:

```bash
uv run uvicorn main:app --reload --host localhost --port 8080
```

The backend will be available at:

- API: `http://localhost:8080/api`
- Health check: `http://localhost:8080/api/healthz`
- Swagger docs: `http://localhost:8080/docs`

Tables are created automatically during startup through SQLAlchemy metadata.

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | Yes | SQLAlchemy database connection string. Use PostgreSQL on Railway. |
| `JWT_SECRET` | Yes | Secret key used to sign JWT access tokens. Use a strong random value in production. |
| `PORT` | Railway sets this | Port the server listens on. Railway injects this automatically. |
| `FRONTEND_ORIGINS` | Yes | Comma-separated list of allowed frontend origins for CORS. |
| `ADMIN_USERNAME` | Recommended | Username for the seeded admin account. |
| `ADMIN_PASSWORD` | Recommended | Password for the seeded admin account. Change this before production use. |
| `ADMIN_FULLNAME` | Recommended | Display name for the seeded admin account. |

Production `FRONTEND_ORIGINS` should include:

```env
FRONTEND_ORIGINS=https://fire-alert-mu.vercel.app
```

Do not include a trailing slash in origins. This is valid:

```env
FRONTEND_ORIGINS=https://fire-alert-mu.vercel.app
```

This is not a valid CORS origin match:

```env
FRONTEND_ORIGINS=https://fire-alert-mu.vercel.app/
```

## Railway Deployment

Deploy this `backend` folder as the Railway service.

This folder includes `railway.json`, so Railway can detect the build and deploy settings automatically.

Deploy from GitHub:

1. Push this backend code to GitHub.
2. In Railway, create a new project.
3. Choose **Deploy from GitHub repo**.
4. Select this repository.
5. If Railway asks for the root directory, set it to `backend`.
6. Deploy the service.
7. Open the service **Settings** tab, go to **Networking**, and generate a public domain.

Railway configuration:

- Root directory: `backend`
- Build command: `pip install .`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/api/healthz`
- Runtime: Python 3.11+

Set these Railway environment variables:

```env
DATABASE_URL=postgresql://...
JWT_SECRET=your-strong-production-secret
FRONTEND_ORIGINS=https://fire-alert-mu.vercel.app
ADMIN_USERNAME=admin
ADMIN_PASSWORD=replace-with-a-secure-password
ADMIN_FULLNAME=Fire Alert Admin
```

Production notes:

- Use Railway PostgreSQL or another managed PostgreSQL database.
- Do not use SQLite in production.
- Keep `JWT_SECRET` private and rotate it if exposed.
- Set `FRONTEND_ORIGINS` exactly to the Vercel frontend domain, plus any custom domain you add later.
- Add the Railway backend URL to Vercel as `VITE_API_BASE_URL=https://fire-alert-backend-production.up.railway.app`.

## Database

The app currently creates tables automatically at startup:

```python
Base.metadata.create_all(bind=engine)
```

This is simple and works for the current schema. For larger production changes, add a migration tool such as Alembic before making breaking database changes.

## Project Layout

```text
backend/
|-- app/
|   |-- auth.py          # Password hashing, JWT signing, auth dependencies
|   |-- database.py      # SQLAlchemy engine/session setup
|   |-- models.py        # Database models
|   |-- schemas.py       # Request/response schemas
|   |-- seed.py          # Admin user seed logic
|   `-- routers/         # API route modules
|-- main.py              # FastAPI application entrypoint
|-- railway.json         # Railway build, start, health check, and restart config
|-- Procfile             # Fallback process command for Python hosts
|-- pyproject.toml       # Python dependencies and package metadata
|-- .env.example         # Local environment template
`-- README.md
```

## Production Checklist

- PostgreSQL database is configured through `DATABASE_URL`.
- `JWT_SECRET` is strong and not committed.
- `ADMIN_PASSWORD` is changed from the default.
- `FRONTEND_ORIGINS` includes the deployed Vercel URL.
- `/api/healthz` returns `{"status":"ok"}` after deployment.
- Frontend `VITE_API_BASE_URL` points to `https://fire-alert-backend-production.up.railway.app`.
