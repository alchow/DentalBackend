# Dental Backend Deployment Guide

> **Last Updated**: 2026-01-30  
> **Audience**: Human operators and AI agents deploying or debugging this system  
> **Production URL**: https://dental-backend-2iw4ademaa-uc.a.run.app

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Cloud Run      │────▶│   Cloud SQL     │
│   (Vercel/etc)  │     │   dental-backend │     │   PostgreSQL    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Cloud Build     │
                        │  (CI/CD Trigger) │
                        └──────────────────┘
                               ▲
                               │
                        ┌──────────────────┐
                        │   GitHub Repo    │
                        │   main branch    │
                        └──────────────────┘
```

---

## Quick Reference

| Resource | Value |
|----------|-------|
| GCP Project ID | `dentaldb-482716` |
| Cloud Run Service | `dental-backend` |
| Cloud Run Region | `us-central1` |
| Cloud SQL Instance | `dentaldb-482716:us-central1:dentaldb` |
| Database Name | `dental_db` |
| Database User | `dental_user` |
| Container Registry | `gcr.io/dentaldb-482716/dental-backend` |

---

## Deployment Methods

### Method 1: Automatic (Git Push)

Push to `main` triggers Cloud Build automatically.

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Cloud Build will:
1. Build Docker image
2. Push to Container Registry
3. Deploy to Cloud Run with env vars from `cloudbuild.yaml`

**Monitor build**: [Cloud Build History](https://console.cloud.google.com/cloud-build/builds?project=dentaldb-482716)

---

### Method 2: Manual Deploy (GCP Console)

Use when you need to change configuration without code changes.

1. Open [Cloud Run Console](https://console.cloud.google.com/run/detail/us-central1/dental-backend/revisions?project=dentaldb-482716)
2. Click **EDIT & DEPLOY NEW REVISION**
3. Modify settings as needed
4. Click **DEPLOY**

---

### Method 3: CLI Deploy

```bash
gcloud run deploy dental-backend \
  --image gcr.io/dentaldb-482716/dental-backend \
  --region us-central1 \
  --platform managed \
  --add-cloudsql-instances dentaldb-482716:us-central1:dentaldb \
  --set-env-vars "DB_HOST=/cloudsql/dentaldb-482716:us-central1:dentaldb,DB_TYPE=postgres,DB_USER=dental_user,DB_NAME=dental_db"
```

---

## Environment Variables

### Required Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `DB_HOST` | `/cloudsql/dentaldb-482716:us-central1:dentaldb` | Cloud SQL socket path |
| `DB_TYPE` | `postgres` | Database type |
| `DB_USER` | `dental_user` | ⚠️ NOT `postgres` |
| `DB_NAME` | `dental_db` | Database name |
| `DB_PASS` | (secret) | Database password |
| `ENCRYPTION_KEY` | (secret) | Fernet key for PII encryption |
| `SECRET_KEY` | (secret) | JWT signing key |

### ⚠️ Common Mistake: Wrong DB_USER

**Wrong**: `DB_USER=postgres`  
**Correct**: `DB_USER=dental_user`

If you see `ConnectionRefusedError` or "password authentication failed" in logs, check this first.

---

## Database Migrations

### Pre-requisites

1. Cloud SQL Proxy running locally
2. Virtual environment activated
3. Correct env vars set

### Step-by-Step

```bash
# 1. Start Cloud SQL Proxy (in separate terminal)
./cloud_sql_proxy -instances=dentaldb-482716:us-central1:dentaldb=tcp:5432

# 2. Set environment variables
export DB_HOST=127.0.0.1
export DB_PORT=5432
export DB_USER=dental_user
export DB_NAME=dental_db
export DB_PASS='4NNLUORbtL!vWRtLec6X1'

# 3. Activate virtual environment
source venv/bin/activate

# 4. Run migrations
cd backend
alembic upgrade head
```

### Verify Migration

```bash
alembic current  # Shows current revision
alembic history  # Shows migration history
```

---

## Troubleshooting

### 500 Internal Server Error

**Check logs**:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=dental-backend AND severity>=ERROR" --limit=10 --format="value(textPayload)"
```

**Common causes**:
1. Wrong `DB_USER` (should be `dental_user`)
2. Wrong `DB_HOST` (should be socket path, not `localhost`)
3. Missing `DB_PASS`
4. Missing database migration

### 403 "Could not validate credentials"

- Check that `SECRET_KEY` env var matches the one used to sign JWTs
- If keys don't match after redeployment, all existing tokens become invalid

### 405 Method Not Allowed

- Check URL path (no trailing slashes)
- Verify endpoint exists in codebase

---

## Verification Checklist

After each deployment:

```bash
# 1. Health check
curl https://dental-backend-2iw4ademaa-uc.a.run.app/health
# Expected: {"status":"ok"}

# 2. Auth test (replace with valid credentials)
curl -X POST https://dental-backend-2iw4ademaa-uc.a.run.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
# Expected: {"access_token": "...", "token_type": "bearer"}

# 3. Protected endpoint test
TOKEN="<token from above>"
curl https://dental-backend-2iw4ademaa-uc.a.run.app/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN"
# Expected: [] or list of tasks
```

---

## File Reference

| File | Purpose |
|------|---------|
| `cloudbuild.yaml` | CI/CD pipeline definition |
| `Dockerfile` | Container build instructions |
| `backend/alembic/` | Database migrations |
| `backend/app/core/config.py` | Environment variable handling |
| `service.yaml` | Cloud Run service export (reference only) |

---

## Console Links

| Resource | Link |
|----------|------|
| Cloud Run Service | [Console](https://console.cloud.google.com/run/detail/us-central1/dental-backend?project=dentaldb-482716) |
| Cloud Build History | [Console](https://console.cloud.google.com/cloud-build/builds?project=dentaldb-482716) |
| Cloud SQL Instance | [Console](https://console.cloud.google.com/sql/instances/dentaldb?project=dentaldb-482716) |
| Secret Manager | [Console](https://console.cloud.google.com/security/secret-manager?project=dentaldb-482716) |
| Container Registry | [Console](https://console.cloud.google.com/gcr/images/dentaldb-482716?project=dentaldb-482716) |
| Logs Explorer | [Console](https://console.cloud.google.com/logs?project=dentaldb-482716) |

---

## For AI Agents

When debugging deployment issues:

1. **First**: Check `DB_USER` and `DB_HOST` env vars
2. **Second**: Check Cloud Run logs for specific error
3. **Third**: Verify migrations are applied (`alembic current`)
4. **Fourth**: Ensure secrets (`DB_PASS`, `SECRET_KEY`, `ENCRYPTION_KEY`) are set

Use `gcloud run services describe dental-backend --region us-central1 --format=yaml` to inspect current configuration.
