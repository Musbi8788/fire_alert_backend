# Contributing to Fire Alert Backend

Thanks for helping improve the Fire Alert backend — the FastAPI service that powers emergency fire reporting for The Gambia. This guide covers **the backend only** (the `backend/` folder). The frontend has its own setup.

Please read [`CLAUDE.md`](./CLAUDE.md) alongside this document — it describes the architecture and conventions in detail. This file tells you *how to contribute*; `CLAUDE.md` tells you *how the code works*.

---

## 1. Ground Rules

- Be respectful and constructive in issues, reviews, and discussions.
- Keep changes **small and focused**. One logical change per pull request.
- Match the existing code style and patterns — don't reformat or refactor unrelated code in the same PR.
- This service handles emergency reports and user accounts. Treat auth, validation, and data handling with care.
- Never commit secrets, real credentials, or production data.

---

## 2. Getting Set Up

You need **Python 3.11+** and the [`uv`](https://github.com/astral-sh/uv) package manager.

```bash
# from the backend/ folder
cp .env.example .env          # then edit values for local dev
uv sync                       # create .venv and install dependencies
uv run uvicorn main:app --reload --host localhost --port 8080
```

Verify it works:

- Health check: `http://localhost:8080/api/healthz` → `{"status":"ok"}`
- Swagger docs: `http://localhost:8080/docs`

Local development uses SQLite (`sqlite:///./firealert.db`); tables are created automatically on first boot. Use `uv` for everything — **never** raw `pip install`.

---

## 3. Contribution Workflow (Fork + Pull Request)

We use a **fork-and-pull-request** model. Direct pushes to `main` are not accepted.

1. **Fork** the repository to your own account.
2. **Clone** your fork and create a branch off `main`:
   ```bash
   git checkout -b feat/admin-report-export
   ```
   Use a short, descriptive branch name (e.g. `feat/...`, `fix/...`, `docs/...`).
3. **Make your change**, following the conventions below.
4. **Run the checks locally** (lint, format, tests — see sections 5 and 6) and make sure they pass.
5. **Commit** with clear messages (see section 4).
6. **Push** to your fork and **open a pull request against `main`** of the upstream repo.
7. A maintainer reviews. Respond to feedback by pushing follow-up commits to the same branch.
8. Once approved, a maintainer merges. Please keep your branch up to date with `main` if it falls behind.

### Pull request expectations

- Fill in **what** changed and **why**. Link any related issue.
- Keep the diff scoped to one concern. Split unrelated work into separate PRs.
- Note any new environment variables, schema changes, or manual steps a reviewer/deployer must take.
- Confirm the checks in section 7 pass before requesting review.

---

## 4. Commit Messages

Write **imperative, descriptive** messages that explain the change and the reason for it. No strict prefix format is required, but the message should make the intent clear.

- First line: a concise imperative summary (~50–72 chars). "Add", "Fix", "Update", "Remove" — not "Added"/"Fixing".
- Optional body: explain the *why*, not just the *what*, and anything non-obvious.

Good:

```
Add `since` filter to admin reports endpoint

Lets the dashboard poll for incidents created after a timestamp
instead of re-fetching the full list on every refresh.
```

Avoid: `update`, `fix stuff`, `wip`, `changes`.

---

## 5. Code Style

We use **[Ruff](https://docs.astral.sh/ruff/)** for both linting and formatting. Run both before you commit:

```bash
uv run ruff check .      # lint
uv run ruff format .     # format
```

> **Note:** if a Ruff config is not yet present in `pyproject.toml`, run the commands with their defaults and match the existing code. If you're setting up tooling, adding a `[tool.ruff]` section in `pyproject.toml` is a welcome contribution.

Conventions specific to this codebase (see `CLAUDE.md` for the full list):

- **Absolute imports** (`from app.auth import ...`), kept sorted.
- **camelCase at the API boundary, snake_case in the DB.** Map between them explicitly in the router serialize helpers — never leak raw model field names into responses.
- **Store UTC** (`datetime.utcnow`); convert to local time only at the presentation layer (the frontend).
- **Explicit transactions:** sessions don't autocommit. Call `db.commit()`, then `db.refresh(obj)` when you need generated values.
- **Structured errors:** raise `HTTPException` with a `{"error": "...", "message": "..."}` detail dict, matching existing handlers.
- **Validation belongs in Pydantic schemas** (`Field(...)` constraints, enums like `ReportStatus`) rather than ad-hoc checks in handlers.
- **Keep route handlers thin.** If logic grows, extract a helper instead of bloating the route.
- Add **type hints** to new function signatures.

---

## 6. Testing

New backend logic must ship with **[pytest](https://docs.pytest.org/)** tests.

```bash
uv run pytest
```

- Any new endpoint or non-trivial logic change needs at least a **happy-path** test and a **failure-path** test (e.g. unauthorized access, validation error, not-found).
- Cover the **auth boundaries**: prove that `require_auth` / `require_admin` actually block the wrong callers, and that users only see their own reports.
- Tests should run against the local SQLite database or an in-memory SQLite instance — never against a real/production database.

> **Note:** the test suite is not bootstrapped yet. If you're the first to add tests, create a top-level `tests/` folder mirroring the `app/` layout, add `pytest` (and `httpx` for FastAPI's `TestClient`) as a dev dependency via `uv add --dev`, and wire up a basic fixture for a test database. This is a high-value first contribution.

If a change genuinely cannot be unit-tested, describe the manual verification steps (via `/docs`) in the PR.

---

## 7. Pre-Submit Checklist

Before opening or updating a pull request, confirm:

- [ ] `uv run ruff check .` passes with no errors.
- [ ] `uv run ruff format .` leaves no changes.
- [ ] `uv run pytest` passes (and new logic has tests).
- [ ] The app still boots: `uv run uvicorn main:app --reload` and `/api/healthz` returns `{"status":"ok"}`.
- [ ] No secrets, real credentials, or production data are committed.
- [ ] API responses keep the camelCase ↔ snake_case mapping intact.
- [ ] New endpoints declare the correct auth dependency (`require_auth` / `require_admin` / public).
- [ ] `README.md` and/or `CLAUDE.md` are updated if behavior, routes, or env vars changed.
- [ ] Commit messages are clear and imperative.

---

## 8. Things That Need Extra Care

These areas are easy to get wrong — flag them explicitly in your PR:

- **Schema changes.** There are **no migrations**; `Base.metadata.create_all` only creates *new* tables and won't alter existing ones. A column added to an existing populated database will **not** apply automatically. If your change touches the schema, call it out and propose a migration path (introducing Alembic is welcome).
- **Auth & JWT.** Changes to token signing, expiry, or the auth dependencies affect every protected route and existing tokens. Discuss before changing.
- **CORS.** To add a frontend origin, update `FRONTEND_ORIGINS` and, if it's a new pattern, the regex in `main.py`. No trailing slashes.
- **Secrets/config.** `JWT_SECRET` and admin credentials come from environment variables. The fallback defaults in `auth.py` and `seed.py` are **dev-only** and must never be relied on in production.

---

## 9. Reporting Bugs & Requesting Features

Open an issue with:

- **Bugs:** what you did, what you expected, what actually happened, and the relevant request/response or error output. Mention whether it's local (SQLite) or production (Railway/Postgres).
- **Features:** the problem you're trying to solve and your proposed approach, so it can be discussed before significant work begins.

For anything touching security (auth, data exposure, secrets), please raise it privately with the maintainers rather than in a public issue.

---

Thanks for contributing! 🔥🚒
