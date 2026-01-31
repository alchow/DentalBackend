# Backend Implementation Knowledge Base

> **Status**: Living Document  
> **Last Updated**: 2026-01-30  
> **Maintainer**: Backend Agent  

This document serves as the primary technical reference for the Dental Backend. It synthesizes architectural decisions, implementation details, and operational knowledge to facilitate agent handoffs.

---

## 1. System Architecture

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ (Cloud SQL)
- **ORM**: SQLAlchemy 2.0 (Async) + Alembic (Migrations)
- **Infrastructure**: Google Cloud Run (Serverless)
- **CI/CD**: Cloud Build (triggers on push to `main`)

### Key Design Patterns
1.  **Async/Await**: Fully async database access via `asyncpg`.
2.  **Dependency Injection**: Heavy use of FastAPI `Depends` for auth and DB sessions.
3.  **Strict Typing**: Pydantic v2 schemas for all IO.

---

## 2. Multi-Tenancy Strategy

The system is a multi-tenant SaaS.

- **Isolation Model**: Row-level security via `office_id` (UUID).
- **Enforcement**:
    - The `get_current_tenant_id` dependency is the **single source of truth**.
    - It resolves the tenant from either JWT (User) or API Key (System).
    - **CRITICAL**: Every endpoint interacting with data MUST verify `office_id`.
- **Global Resources**: `users` and `offices` are global but linked.

---

## 3. Authentication & Authorization

Dual authentication strategy (Hybrid):

### A. Frontend Users (Human)
- **Method**: Bearer Token (JWT).
- **Flow**: `POST /auth/login` -> Returns Access Token.
- **Expiry**: 8 days (default).
- **Roles**: `ADMIN`, `USER`.
- **Password Reset**: Admin-initiated (see "Recent Features").

### B. System Integrations (Machine)
- **Method**: API Key (`X-Office-Key` header).
- **Storage**: Hashed (SHA256) in `api_keys` table.
- **Prefix**: `sk_live_...` (visible), rest hidden.

---

## 4. Data Privacy & Encryption (HIPAA)

We treat Patient PII as sensitive.

- **Encryption at Rest**:
    - `first_name`, `last_name`, `contact_info` (JSON) are encrypted using **Fernet** (symmetric).
    - Key: `ENCRYPTION_KEY` env var.
- **Searching Encrypted Data**:
    - We use **Blind Indexes** (deterministic SHA256 hashes).
    - Columns: `last_name_hash`, `first_name_hash`, `phone_hash`.
    - **Strategy**: Creating a patient populates both encrypted text AND hashes. Searching queries the hash.

---

## 5. Recent Features (Jan 30 2026)

### A. Enhanced Patient Search
- **Capability**: Search by First Name, Last Name, and Phone.
- **Implementation**: Added `*_hash` columns + indexes.
- **Endpoint**: `GET /api/v1/patients/search/query` (AND logic for params).

### B. Visit Duration
- **Field**: `duration_minutes` (Integer).
- **Default**: 30 minutes.
- **Logic**: Frontend calculates `End Time = Start Time + Duration`.

### C. Password Reset Logic
- **No Email Service**: We currently lack SendGrid/SES.
- **Flow**:
    1. Admin calls `POST /auth/admin-reset-password` -> Gets a link.
    2. Admin sends link to user (manually via Slack/Email/SMS).
    3. User clicks link -> Frontend calls `POST /auth/reset-password` with token.

---

## 6. Operational & Deployment

### GCP Deployment
- **Method**: `cloudbuild.yaml` automated pipeline.
- **Environment Variables**:
    - **CRITICAL**: `DB_USER` must be `dental_user` (NOT `postgres`).
    - **CRITICAL**: `DB_HOST` in Cloud Run must be the socket path `/cloudsql/project:region:instance`.
- **Troubleshooting**: If 500 errors occur on deploy, check `DB_USER` first.

### Verification
- **Script**: `./scripts/verify_deployment.sh`
- **Scope**: Runs full E2E test suite (`tests/e2e/test_live_api.py`) against production.

---

## 7. Handoff: How to Pick Up Work

If you are a new agent starting on this repo:

1.  **Read the Specs**:
    - `docs/frontend_api_spec.md` (Contract)
    - `docs/FRONTEND_API_GUIDE.md` (Integration patterns)
2.  **Check Configuration**:
    - `backend/app/core/config.py` contains all env var logic.
3.  **Run Tests First**:
    - Local: `./scripts/verify_deployment.sh` (can run against local too if configured).
4.  **Database Changes**:
    - ALWAYS use Alembic. Never edit DB manually.
    - `alembic revision --autogenerate -m "message"`
    - `alembic upgrade head`

### Known Technical Debt / Backlog
- **Token Refresh**: Currently missing. Tokens hard-expire in 8 days.
- **Notifications**: No backend support yet (bell icon is static).
- **Email**: No SMTP/Email provider integration.
