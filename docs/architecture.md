# Architecture and decision log

Modular monolith: React/TypeScript/Vite/Tailwind frontend, FastAPI/Pydantic/SQLAlchemy backend, PostgreSQL 16, optional Gemini via backend-only adapter. Docker Compose is the local runtime. Week 1 is a vertical slice, with deferred features explicitly labeled.

## Dependencies

Authentication and authorization precede ticket access. Tickets precede classification; classification precedes department-scoped agent access and draft generation. Workflow state machine and approvals precede outbox. Persisted events precede analytics and reports. Historical data precedes forecasting.

## Pending decisions

Requester reopening policy; minimum group size for confidential aggregated metrics; confidential membership escalation; approval edits and authorship; outbox retry strategy; precise priority taxonomy and escalation thresholds; transactional idempotency design.

## Deployment risks

No public production deployment until authentication hardening, privacy protections, complete authorization matrix, login/AI rate limiting, CSRF/cookie security, audit events, concurrency controls, and full integration tests pass.
