# Backend Implementation Knowledge Base

> **Status**: Living Document  
> **Last Updated**: 2026-02-02  
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

## 3. CORS Configuration
 
The backend enforces strict CORS but allows specific subdomains for integrations.
 
- **Middleware**: `starlette.middleware.cors.CORSMiddleware`
- **Configuration**:
    - **Localhost**: `http://localhost:3000`
    - **Production Frontend**: `https://dental-frontend-*.run.app`
    - **Lovable Integrations**: `https://*.lovable.app`, `https://*.lovableproject.com` (via Regex)
- **Regex Logic**: `r"^https://.*\.lovable(project)?\.(app|com)$"` handles dynamic preview URLs.
 
---
 
## 4. Authentication & Authorization

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

### D. Clinical Notes API Enhancement (Jan 31 2026)
- **Purpose**: Support "Charts" feature for browsing/searching clinical notes.
- **New Endpoints**:
    - `GET /api/v1/notes` - Paginated list with filtering (note_type, patient_id, visit_id, date range)
    - `GET /api/v1/notes/{id}` - Single note lookup with 404/403 error handling
- **Features**:
    - `include_patient=true` optional JOIN to avoid N+1 queries
    - Pagination format: `{items, total, limit, offset}`
    - Content auto-decrypted in responses
- **Schemas Added**: `PatientSummary`, `NoteWithPatient`, `NoteListResponse`

### E. Note History API (Feb 1 2026)
- **Purpose**: View edit history for clinical notes (version control).
- **New Endpoint**: `GET /api/v1/notes/{id}/history`
- **Features**:
    - Returns all prior versions, newest-first
    - Content auto-decrypted in responses
    - Full tenant isolation (404/403 error handling)
- **Schemas Added**: `NoteHistoryItem`, `NoteHistoryListResponse`

### F. Backfill API (Feb 1 2026)
- **Purpose**: Import historical data with custom `created_at` timestamps.
- **New Endpoints**:
    - `POST /api/v1/backfill/patients`
    - `POST /api/v1/backfill/visits`
    - `POST /api/v1/backfill/notes`
    - `POST /api/v1/backfill/bills`
- **Features**:
    - **API-key only auth** (rejects Bearer tokens)
    - `created_at` must be in the past (validation)
    - `is_backfilled=true` flag for audit trail
- **Files Added**: 
    - `app/schemas/backfill.py`
    - `app/api/v1/endpoints/backfill.py`
- **Migration**: `20260201_add_backfill_flag.py` adds `is_backfilled` to 4 tables

### G. SSN Patient Identification & Duplicate Detection (Feb 1 2026)
- **Purpose**: Flexible SSN input (full, last-4, or none) with duplicate warning before creation.
- **New Fields** (Patient model):
    - `ssn_encrypted` (Fernet encrypted)
    - `ssn_hash` (blind index for full SSN)
    - `last_4_ssn_hash` (blind index for last-4)
- **New Endpoints**:
    - `GET /api/v1/patients/search/ssn` - Search by SSN
    - `POST /api/v1/patients/check-duplicate` - Soft duplicate warning
- **Response field**: `ssn_last_4` (masked: `***-**-1234`)
- **Duplicate Confidence Levels**: HIGH (SSN exact), MEDIUM (last-4+DOB+name), LOW (phone+name)
- **Migration**: `20260201_add_ssn_fields.py`

### H. Backfill Bills Async Fix (Feb 1 2026)
- **Issue**: `POST /backfill/bills` 500 error due to SQLAlchemy lazy loading in async context
- **Fix**: Replaced `db_bill.codes.append()` with raw SQL insert into `bill_codes_association` table
- **File**: `app/api/v1/endpoints/backfill.py`

### I. Task Assignee Type (Feb 1 2026)
- **Purpose**: Distinguish tasks for dentist vs patient vs front desk.
- **New Field**: `assignee_type` (String: `DENTIST`, `PATIENT`, `FRONT_DESK`)
- **Default**: `DENTIST` (existing tasks backfilled with this value)
- **Usage**: Filter tasks by audience: `GET /tasks?assignee_type=PATIENT`
- **Migration**: `20260201_add_task_assignee_type.py`

### J. Patient Summary with LLM Integration (Feb 2 2026)
- **Purpose**: AI-generated patient summaries with history, manual edit support
- **New Table**: `patient_summaries` (encrypted content, source, model info, audit)
- **Endpoints**:
    - `GET /api/v1/patients/{id}/summary` - Latest summary
    - `GET /api/v1/patients/{id}/summary/history` - Paginated history
    - `PUT /api/v1/patients/{id}/summary` - Manual edit
    - `POST /api/v1/internal/generate-summary` - Cloud Tasks webhook
- **LLM Abstraction**: `app/services/llm_service.py` - Swappable OpenAI/Gemini/Anthropic
- **Prompt Versioning**: `backend/prompts/` directory with `config.yaml`
- **Cloud Tasks**: `app/services/task_queue.py` with configurable debounce
- **Migration**: `20260202_add_patient_summaries.py`

### K. Schema Cleanup: PatientSummary → PatientEmbed (Feb 2 2026)
- **Purpose**: Rename to avoid confusion with new `patient_summaries` table
- **Change**: `PatientSummary` schema in `visit_note.py` renamed to `PatientEmbed`
- **Impact**: Lightweight patient embed in `NoteWithPatient` responses

### L. Remove Unused Visit Summary (Feb 2 2026)
- **Purpose**: Remove unused `visit.summary` column (replaced by `patient_summaries`)
- **Removed from**: `visit.py` model, `visit_note.py` schemas
- **Migration**: `20260202_remove_visit_summary.py`

### M. Prompt V2 and Model Updates (Revision 00037)

**Model Change:**
- Default OpenAI model: `gpt-4o-mini`
- **Configurable** via `LLM_MODEL` env var (no redeploy needed)
- Example: Set `LLM_MODEL=gpt-5-mini` when API key has access

**Prompt V2 (Pre-Visit Huddle):**
- Path: `prompts/patient_summary/v2.txt`
- Output: Markdown format with sections for 60-second snapshot, changes since last visit, open loops, risks, plan options, and questions
- Response stored in `content.summary_markdown` field

**Date Context:**
- Notes prefixed with `[YYYY-MM-DD]` before sending to LLM
- Enables chronological reasoning and date-specific extraction

**Cloud Tasks Integration:**
- Queue: `dental-summary-queue` (us-central1)
- Trigger: `enqueue_summary_generation()` called after note creation
- Dependencies: `google-cloud-tasks>=2.14.0` in requirements.txt

**Sync Local Mode (Feb 2 2026):**
- For local development without Cloud Tasks, set `SUMMARY_SYNC_MODE=true`
- Generates summary synchronously in request thread (~1-2s delay on note creation)
- Uses `get_db_session()` context manager from `app/db/session.py`
- Logs all operations for debugging (check `logger` output)

**GCP Verification (Feb 2 2026):**
- Summary pipeline verified working end-to-end on Cloud Run
- LLM generation takes ~8-10 seconds via `gpt-4o-mini`
- E2E tests poll for 30s to accommodate async Cloud Tasks + LLM latency
- All patient summary endpoints tested: GET, PUT, history

**Schema Fix (Feb 2 2026 - Revision 00048):**
- **Bug**: `SummaryContent` Pydantic schema was missing `summary_markdown` field
- **Impact**: AI summaries returned `{"summary_markdown": null, ...}` to frontend
- **Root Cause**: LLM correctly stored `{"summary_markdown": "..."}` in DB, but Pydantic dropped it during serialization because field wasn't in schema
- **Fix**: Added `summary_markdown` and additional fields to `app/schemas/summary.py`
- **Deployed**: Revision `dental-backend-00048-hcl` contains the fix

**Environment Variables:**
| Variable | Description | Default |
|----------|-------------|---------|
| `CLOUD_TASKS_QUEUE` | Queue name for async mode | (none) |
| `SUMMARY_SYNC_MODE` | Enable sync local generation | `false` |
| `SUMMARY_DEBOUNCE_SECONDS` | Debounce interval | `300` |
| `LLM_MODEL` | Override default model | `gpt-4o-mini` |

---

## 6. Operational & Deployment

### GCP Deployment
- **Method**: `cloudbuild.yaml` automated pipeline.
- **Environment Variables**:
    - **CRITICAL**: `DB_USER` must be `dental_user` (NOT `postgres`).
    - **CRITICAL**: `DB_NAME` must be `dental_db` (NOT `dental_notes` which is for local dev).
    - **CRITICAL**: `DB_HOST` in Cloud Run must be the socket path `/cloudsql/project:region:instance`.
- **Troubleshooting**: If 500 errors occur on deploy, check `DB_USER` and `DB_NAME` first.

### Verification
- **Scripts**:
    - `./scripts/verify_gcp.sh`: **Primary**. Runs `tests/e2e/test_live_api.py` against production.
    - `./scripts/migrate_prod.sh`: **Primary**. Safely runs Alembic migrations against production DB.
- **Scope**: Runs full E2E test suite (`tests/e2e/test_live_api.py`) against production.

---

## 7. Security Hardening (Feb 8 2026)

### A. Fail-Fast on Missing Secrets
- `ENCRYPTION_KEY` and `SECRET_KEY` now crash on startup if not set.
- **Local dev**: Set `ALLOW_INSECURE_DEFAULTS=true` to use hardcoded dev keys.
- Production always requires real keys via Secret Manager.

### B. Internal Endpoint Authentication
- `/api/v1/internal/generate-summary` now requires `X-Internal-Key` header.
- Key stored in GCP Secret Manager as `INTERNAL_API_KEY`.
- Cloud Tasks must send this header when calling the endpoint.
- TODO: Migrate to OIDC token verification.

### C. Tenant Isolation on Summaries
- `get_latest_summary()` and `get_summary_history()` now filter by `office_id`.
- Previously, only `patient_id` was checked, allowing cross-tenant reads.

### D. Removed PHI Debug Logging
- Removed `[DEBUG:SUMMARY]` log lines that logged unencrypted patient summaries.
- Replaced with safe, non-PHI log lines for tracing.

---

## 8. Handoff: How to Pick Up Work

If you are a new agent starting on this repo:

1.  **Read the Specs**:
    - `docs/frontend_api_spec.md` (Contract)
    - `docs/FRONTEND_API_GUIDE.md` (Integration patterns)
2.  **Check Configuration**:
    - `backend/app/core/config.py` contains all env var logic.
    - Set `ALLOW_INSECURE_DEFAULTS=true` for local development.
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
- **OIDC for Internal Endpoints**: Currently using shared secret; should migrate to OIDC token verification.
- **MCP Server Tenancy**: MCP server (`mcp/server.py`) queries without `office_id` filter — dev tool only.
- **Datetime Consistency**: Mixed use of `datetime.utcnow`, `datetime.now(timezone.utc)`, and `func.now()` across models.
- **Rate Limiting**: No rate limiting on any endpoint (consider Cloud Armor).

