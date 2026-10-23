# OpsPilot — Week 1 foundation

Synthetic-data-only demonstration. No actual email delivery.

## Start

1. Copy `.env.example` to `.env`; set `POSTGRES_PASSWORD` and `SECRET_KEY` (use a long random secret).
2. `docker compose build`
3. `docker compose up -d db`
4. `docker compose run --rm backend alembic upgrade head`
5. `docker compose run --rm backend python scripts/seed_demo.py`
6. `docker compose up -d backend frontend`
7. Open http://localhost:5173; API docs: http://localhost:8000/docs

Seeded synthetic users: `requester@demo.local`, `agent.it@demo.local`, `lead.it@demo.local`, `agent.hr@demo.local`, `lead.hr@demo.local`, `administrator@demo.local`. Demo-only password: `DemoOnly!2026`. Never deploy these accounts or credentials publicly.

The requester can submit, list and view their tickets and initiate classification. An IT agent can view classified nonconfidential IT tickets and generate drafts. Sensitive HR/Wellness/Legal content requires explicit grants, including for administrators. Approval and delivery are **not implemented** in Week 1.

Offline AI is the default. For live Gemini set `DEMO_MODE=false` and `GEMINI_API_KEY`; this is not recommended for synthetic public demonstrations. The provider adapter does not automatically transmit real personal data intentionally; never submit real employee records.

## Status and limitations

This is a **Week 1 implementation scaffold, not a verified production application**. Ticket CRUD is partial (create/list/detail), and there is no safe manual review override UI yet. The API does not yet support ticket updates, approval, notification delivery, PDF, forecasting, analytics, comprehensive risk checks, pagination, login rate limits, or token revocation. Classification is invoked explicitly rather than automatically after submission. Offline fallback is a keyword-based heuristic, not an accuracy-evaluated classifier. The Week 1 schema contains future module tables, but those modules are not functional.

Security TODO: move token handling from sessionStorage to secure HttpOnly cookies with CSRF protection, add server-side logout/revocation, robust idempotency table, audit of denied access, request size/rate limits, approval of grants, strict confidential policies, migration verification, and tests with real PostgreSQL. Do not expose this scaffold on the public internet.
