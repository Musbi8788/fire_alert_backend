# Security Policy

This policy covers the **Fire Alert backend** — the FastAPI service in this `backend/` folder that handles user accounts, authentication, and emergency fire reports for The Gambia. Because this service stores personal data (names, phone numbers) and location data tied to real incidents, we take security reports seriously.

---

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.** Public disclosure before a fix is available puts users at risk.

Instead, report privately to:

📧 **musbimusbi7@gmail.com**

Include as much of the following as you can:

- A description of the vulnerability and its impact.
- Steps to reproduce (proof-of-concept request, payload, or script).
- The affected endpoint(s), file(s), or component.
- Whether it was found locally (SQLite) or against production (Railway/PostgreSQL).
- Any suggested remediation.

### What to expect

- **Acknowledgement** within **3 business days**.
- An initial **assessment and severity rating** within **7 business days**.
- Progress updates as we work on a fix, and credit for the disclosure if you'd like it.

Please give us a reasonable window to release a fix before any public disclosure. We support **coordinated disclosure** and will work with you on timing.

---

## Supported Versions

This is an actively developed, single-track project. Only the **latest `main`** (and the currently deployed production build) receives security fixes. There are no maintained older release branches.

| Version | Supported |
| --- | --- |
| `main` / latest deploy | ✅ |
| Older commits / forks | ❌ |

---

## Scope

**In scope:**

- The FastAPI application in `backend/` (auth, reports, admin, user management).
- Authentication and authorization logic (`app/auth.py`).
- Input validation and data handling in routers and schemas.
- Configuration that affects security (CORS, environment handling, secrets management).

**Out of scope:**

- The frontend application (reported separately).
- Third-party platforms themselves (Railway, Vercel, PostgreSQL) — report infrastructure issues to the respective vendor.
- Vulnerabilities requiring physical access to a developer's machine, or that depend on already-compromised credentials.
- Findings that rely on running with the **documented dev-only insecure defaults** (see below) rather than a correctly configured production deployment.
- Denial-of-service via volumetric traffic / load.

---

## Security Model Overview

For context when assessing reports, the service works as follows:

- **Authentication** is stateless JWT (HS256) via a bearer token, signed with `JWT_SECRET`. Tokens carry `userId`, `username`, and `isAdmin` claims.
- **Authorization** is enforced by FastAPI dependencies: `require_auth` (valid token → user) and `require_admin` (user must have `is_admin`). Admin-only routes live under `/api/admin`.
- **Passwords** are hashed with bcrypt; plaintext passwords are never stored or logged.
- **Input validation** is handled by Pydantic schemas (length limits, typed fields, the `ReportStatus` enum).
- **CORS** is restricted to configured frontend origins (`FRONTEND_ORIGINS`) plus a regex allowlist for local dev and Vercel preview domains; credentials are not sent via cookies (auth is bearer-header based).
- **Transport security** is provided by the hosting platform (HTTPS on Railway/Vercel).

---

## Deployment Security Requirements

The repository ships with **dev-only insecure defaults** so the app runs locally out of the box. These **must** be overridden in any real deployment. Running production with these defaults is a misconfiguration, not a vulnerability in the code:

- **`JWT_SECRET`** — must be set to a strong, random, secret value. There is a hardcoded fallback in `app/auth.py` intended only for local development. If `JWT_SECRET` is ever exposed, **rotate it immediately** (this invalidates all existing tokens).
- **Admin credentials** — `ADMIN_USERNAME` / `ADMIN_PASSWORD` / `ADMIN_FULLNAME` must be set to non-default values. The seed defaults in `app/seed.py` are for local development only.
- **`DATABASE_URL`** — use a managed PostgreSQL instance in production. Do not use SQLite in production.
- **`FRONTEND_ORIGINS`** — set to the exact deployed frontend origin(s), no trailing slashes. Don't widen CORS beyond what's required.
- **Secrets** must come from environment variables only — never commit real secrets, credentials, or production data to the repository.

See `README.md` and `CLAUDE.md` for the full configuration reference.

---

## Known Hardening Opportunities

These are known and tracked, not secret. We welcome reports or PRs that improve them:

- **Long token lifetime:** access tokens currently expire after ~50 days, and there is no refresh/revocation mechanism. A leaked token is valid until expiry. Rotating `JWT_SECRET` is the current way to invalidate all tokens.
- **No rate limiting:** authentication endpoints (`/api/users/login`, `/api/users/register`) are not currently rate-limited, so they are more exposed to brute-force/credential-stuffing attempts. Consider a reverse-proxy or application-level limiter in production.
- **No account lockout** on repeated failed logins.

If you find an issue in one of these areas, a report is still useful — especially anything that increases impact beyond what's described here.

---

## Good-Faith Research

We will not pursue or support legal action against researchers who:

- Make a good-faith effort to avoid privacy violations, data destruction, and service disruption.
- Only interact with accounts they own or have explicit permission to test.
- Do not access, modify, or exfiltrate other users' data beyond the minimum needed to demonstrate the issue.
- Give us a reasonable time to remediate before public disclosure.

Thank you for helping keep Fire Alert and its users safe. 🔥🚒
