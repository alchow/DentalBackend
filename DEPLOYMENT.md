# Deployment Guide

**Project**: Dental Notes Backend (@dentaldb-482716)
**Region**: `us-central1`

This document outlines how to deploy the backend to Google Cloud Platform (GCP). It is written to be executable by developers and understandable by LLM agents.

---

## 🚀 1. Routine Deployment (Git)

The primary deployment method is **Automated CI/CD** via Google Cloud Build.

**Trigger**: Push to `main` branch.

```bash
# 1. Stage changes
git add .

# 2. Commit
git commit -m "feat: your amazing feature"

# 3. Deploy
git push origin main
```

**What happens next:**
1.  GitHub notifies Cloud Build.
2.  Cloud Build uses `cloudbuild.yaml`.
3.  Builds Docker image -> Pushes to GCR.
4.  Deploys to Cloud Run service `dental-backend`.
5.  **Preserves Secrets**: Existing secrets (`DB_PASS`, `SECRET_KEY`, etc.) are preserved.

---

## 🛠 2. Manual Deployment (Fallback)

If CI/CD fails or you need to force a manual update from your local machine.

### Prerequisites
- `gcloud` CLI installed and authenticated (`gcloud auth login`).
- Project set: `gcloud config set project dentaldb-482716`.

### Command
Execute this exact command to deploy the current folder:

```bash
gcloud builds submit --tag gcr.io/dentaldb-482716/dental-backend .
gcloud run deploy dental-backend \
  --image gcr.io/dentaldb-482716/dental-backend \
  --region us-central1 \
  --platform managed \
  --add-cloudsql-instances dentaldb-482716:us-central1:dentaldb \
  --update-env-vars DB_HOST=/cloudsql/dentaldb-482716:us-central1:dentaldb,DB_TYPE=postgres,DB_USER=postgres,DB_NAME=dental_db
```

> **Note**: This command uses `--update-env-vars` to ensure we do **not** overwrite the sensitive secrets (`DB_PASS`, `KEYS`) matched in the active revision.

---

## 🤖 3. LLM Context (System Architecture)

**For AI Agents helping with DevOps:**

- **GCP Project ID**: `dentaldb-482716`
- **Cloud Run Service**: `dental-backend`
- **Cloud SQL Instance**: `dentaldb-482716:us-central1:dentaldb`
- **Database Name**: `dental_db`
- **Socket Path**: `/cloudsql/dentaldb-482716:us-central1:dentaldb` (Used in `DB_HOST`)
- **Secrets Management**: Secrets were manually injected into the Cloud Run environment variables. They are NOT in `cloudbuild.yaml`.
  - To view (hidden): `gcloud run services describe dental-backend --format="yaml"`
  - To update secrets: You must use `gcloud run deploy ... --update-env-vars SECRET_NAME=NEW_VALUE`.

---

## 🔍 4. Verification

After deployment, verify the service is healthy:

1.  **Check Status**:
    ```bash
    gcloud run services describe dental-backend --region us-central1 --format="value(status.url)"
    ```
2.  **Health Check**:
    ```bash
    curl $(gcloud run services describe dental-backend --region us-central1 --format="value(status.url)")/health
    # Expected: {"status": "ok"}
    ```
