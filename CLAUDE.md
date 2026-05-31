# CLAUDE.md — Fire Alert Backend

Guidance for AI agents working in this repository. Read this first.

---

## 1. What This Is

Fire Alert is an emergency fire-reporting platform for **The Gambia**. Citizens register, submit fire reports with GPS coordinates, and view their report history. Administrators see all incidents in a command-center dashboard, filter by status, update statuses, and read aggregate stats.

This folder (`backend/`) is the **FastAPI** API service. It is deployed on **Railway**; the frontend (separate `frontend/` folder) is a Vite/React app deployed on **Vercel**.

- Live frontend: https://fire-alert-mu.vercel.app/
- Production API: https://fire-alert-backend-production.up.railway.app/

---

## 2. Tech Stack

| Concern | Choice |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI (ASGI, served by Uvicorn) |
| ORM | SQLAlchemy 2.0 (declarative, sync engine) |
| Database | PostgreSQL in production, SQLite for local dev |
| Auth | JWT via `python-jose` (HS256) |
| Passwords | `bcrypt` (direct, plus `passlib[bcrypt]` available) |
| Validation | Pydantic v2 schemas |
| Package manager | **`uv`** — never raw `pip install` for local dev |
| Migrations | **None.** Tables are auto-created at startup via `Base.metadata.create_all`. |

---

## 3. Project Layout

```
backend/
├── main.py              # FastAPI app factory: lifespan, CORS, router mounting
├── app/
│   ├── database.py      # engine, SessionLocal, Base, get_db() dependency
│   ├── models.py        # SQLAlchemy models: User, FireReport
│   ├── schemas.py       # Pydantic request/response models (camelCase fields)
│   ├── auth.py          # password hashing, JWT sign/decode, auth dependencies
│   ├── seed.py          # seeds default admin user on startup
│   └── routers/
│       ├── home.py      # GET /            (welcome + timestamp)
│       ├── health.py    # GET /api/healthz (health check)
│       ├── users.py     # /api/users/*     (register, login)
│       ├── reports.py   # /api/reports     (create + list own reports)
│       └── admin.py     # /api/admin/*     (admin reports, status, stats)
├── pyproject.toml       # dependencies + project metadata
├── railway.json         # Railway build/deploy/healthcheck config
├── Procfile             # fallback start command
├── .env.example         # local environment template
└── firealert.db         # local SQLite database (dev only — do not commit data)
```

There is no `services/` or `repositories/` layer. Business logic currently lives directly in router functions. Keep handlers small; if logic grows, propose extracting a helper before bloating a route.

---

## 4. Architecture & Conventions

### Routing
- All API routers are mounted under `/api` (except `home` at `/`). Prefixes are applied in `main.py` via `include_router(..., prefix=...)` — **do not** repeat the prefix inside the router.
- `redirect_slashes=False` is set. Route paths must match exactly: e.g. reports is `""` (becomes `/api/reports`), not `"/"`. Be careful with trailing slashes.
- Each router declares its own `tags=[...]` for the OpenAPI docs at `/docs`.

### Database access
- Inject a session with `db: Session = Depends(get_db)`. The dependency yields a session and closes it in `finally`.
- Sessions are `autocommit=False, autoflush=False` — you must call `db.commit()` explicitly, then `db.refresh(obj)` if you need server-side defaults/IDs.
- `postgres://` URLs are auto-rewritten to `postgresql://` in `database.py` (Railway compatibility).
- SQLite gets `check_same_thread=False`; Postgres gets `pool_pre_ping=True`.

### Models (`models.py`)
- `User`: `id, username (unique), password_hash, full_name, phone (nullable), is_admin, created_at`.
- `FireReport`: `id, user_id (FK→users.id), description, latitude, longitude, address (nullable), status, notes (nullable), created_at, updated_at`.
- `status` is a free-text string column with values `pending` | `in-progress` | `resolved` (default `pending`). The allowed set is enforced at the API layer via the `ReportStatus` enum, not in the DB.
- Timestamps use `datetime.utcnow` — **store UTC**, format/convert at the presentation layer.

### Schemas (`schemas.py`)
- **API field names are `camelCase`** (`fullName`, `userId`, `isAdmin`, `createdAt`, `inProgress`) to match the JS/React frontend. The DB columns are `snake_case`. Routers map between them explicitly in `_user_profile` / `_serialize` helpers — keep this mapping when adding fields.
- Timestamps are serialized as ISO 8601 strings (`.isoformat()`), not raw datetimes, in `FireReport`/`UserProfile` responses.
- `ReportStatus` enum is the source of truth for valid statuses. Use `.value` when assigning to the model (`report.status = body.status.value`).
- Validation lives in `Field(...)` constraints: username 3–50 chars, password ≥6, description ≥10.

### Auth (`auth.py`)
- Bearer token via `HTTPBearer(auto_error=False)`. Tokens are signed with `JWT_SECRET`, HS256, **50-day** expiry.
- JWT payload uses camelCase claims: `userId`, `username`, `isAdmin`, `exp`.
- Two dependencies:
  - `require_auth` → returns the current `User`, 401 on missing/invalid token.
  - `require_admin` → builds on `require_auth`, 403 if `is_admin` is false.
- Protect any user-scoped route with `current_user: User = Depends(require_auth)`; admin-only routes with `Depends(require_admin)`.

### Error responses
- Raise `HTTPException` with a structured detail dict: `{"error": "<Title>", "message": "<human readable>"}`. Match this shape for consistency with existing handlers and the frontend.

### Startup (`main.py` lifespan)
- On startup: `Base.metadata.create_all(bind=engine)` then `seed_admin_user()`. There are no migrations — new model columns appear only on a fresh table. **Adding a column to an existing populated DB will NOT alter it automatically.** If a schema change must apply to existing data, call it out and plan a manual migration (Alembic is recommended but not yet set up).

---

## 5. Running Locally

```bash
# from backend/
cp .env.example .env          # then edit values
uv sync                       # install deps into .venv
uv run uvicorn main:app --reload --host localhost --port 8080
```

- API base: `http://localhost:8080/api`
- Health check: `http://localhost:8080/api/healthz` → `{"status":"ok"}`
- Swagger docs: `http://localhost:8080/docs`

Local dev uses SQLite (`sqlite:///./firealert.db`). Tables are created on first boot.

---

## 6. Environment Variables

| Variable | Required | Notes |
|---|---|---|
| `DATABASE_URL` | Yes | SQLAlchemy URL. Postgres in prod, SQLite locally. App raises at startup if unset. |
| `JWT_SECRET` | Yes (prod) | Token signing key. Has an insecure hardcoded fallback in `auth.py` — **must** be set to a strong value in production. |
| `PORT` | Railway sets it | Server listen port. |
| `FRONTEND_ORIGINS` | Yes | Comma-separated CORS allowlist. **No trailing slashes.** |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` / `ADMIN_FULLNAME` | Recommended | Seed admin credentials. Insecure defaults exist in `seed.py` — override in prod. |

CORS additionally allows any `localhost`/`127.0.0.1:port` and any `*.vercel.app` preview via `allow_origin_regex` in `main.py`. `allow_credentials=False` (auth is via bearer header, not cookies).

---

## 7. API Surface

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/` | none | Welcome message + timestamp |
| `GET` | `/api/healthz` | none | Health check |
| `POST` | `/api/users/register` | none | Register, returns `{token, user}` |
| `POST` | `/api/users/login` | none | Login, returns `{token, user}` |
| `POST` | `/api/reports` | user | Create a fire report |
| `GET` | `/api/reports` | user | List the caller's own reports |
| `GET` | `/api/admin/reports` | admin | All reports; `?status=` and `?since=` (ISO) filters |
| `PATCH` | `/api/admin/reports/{report_id}/status` | admin | Update status + optional notes |
| `GET` | `/api/admin/stats` | admin | Totals by status |

---

## 8. Rules of Engagement

1. **Match existing patterns.** New endpoints follow the router → `Depends(get_db)` → explicit commit → serialize-helper flow. Keep handlers thin.
2. **camelCase at the API boundary, snake_case in the DB.** Maintain the explicit mapping in serialize helpers; never leak raw model field names into responses.
3. **Store UTC.** Use `datetime.utcnow`. Convert to local time only for display (frontend's job).
4. **Protect routes deliberately.** Decide `require_auth` vs `require_admin` vs public for every new endpoint, and enforce ownership where data is user-scoped.
5. **No secrets in the repo.** `JWT_SECRET`, admin passwords, and real `DATABASE_URL` come from env. The fallbacks in `auth.py`/`seed.py` are dev-only and must never be relied on in production. Flag any committed secret.
6. **Mind the no-migrations reality.** Schema changes only take effect on fresh tables. For changes to existing data, propose a migration strategy (introduce Alembic) rather than silently relying on `create_all`.
7. **Validate at the schema layer.** Add Pydantic `Field` constraints / enums rather than ad-hoc checks in handlers where possible.
8. **Keep CORS tight.** When adding a frontend origin, update `FRONTEND_ORIGINS` and, if it's a new pattern, the regex in `main.py`. No trailing slashes.
9. **Stay in scope.** This is a small focused service. Don't introduce Celery, Redis, background workers, or framework changes without discussion.

---

## 9. Known Gaps & Watch-Outs

- **No tests.** There is no test suite or test runner configured. If you add meaningful logic, propose adding `pytest` and tests for it.
- **No Alembic / migrations.** Documented above — the single biggest footgun for schema changes.
- **Insecure default secrets** in `auth.py` (`JWT_SECRET` fallback) and `seed.py` (`musbi`/`musbi123`). These are acceptable only for local dev.
- **`RegisterRequest.phone` is typed `Optional[int]`** but the model/`UserProfile` treat phone as a string. Numbers with leading zeros or `+` country codes will not round-trip cleanly — worth fixing if phone handling matters.
- **No pagination** on `/api/admin/reports`; it returns all rows. Fine at current scale, revisit if report volume grows.
- **`firealert.db`** is a committed local SQLite file — local dev artifact, not production data.

---

## 10. Deployment (Railway)

Config lives in `railway.json`:
- Builder: Nixpacks, build command `pip install .`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health check: `/api/healthz` (300s timeout), restart `ON_FAILURE` (max 10 retries)

Set root directory to `backend` in the Railway service. Provide all required env vars (esp. a strong `JWT_SECRET`, a Postgres `DATABASE_URL`, and the exact Vercel `FRONTEND_ORIGINS`). `Procfile` is a fallback for other Python hosts.
