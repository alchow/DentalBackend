#!/bin/bash
set -e

APP_NAME="dental-backend"
REGION="us-central1"
PROJECT_ID=$(gcloud config get-value project)

if [ -z "$PROJECT_ID" ]; then
    echo "Error: behaviors Cloud SDK project not set."
    echo "Run 'gcloud config set project <PROJECT_ID>' first."
    exit 1
fi

echo "Deploying $APP_NAME to project $PROJECT_ID in $REGION..."

# 1. Enable APIs
echo "Enabling necessary APIs..."
gcloud services enable run.googleapis.com \
                       sqladmin.googleapis.com \
                       secretmanager.googleapis.com \
                       artifactregistry.googleapis.com

# 2. Build and Push (using Cloud Build for simplicity)
echo "Building container image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$APP_NAME .

# 3. Create Secrets (Prompt user if not exist)
# NOTE: This part is tricky to script non-interactively without user input.
# For now, we assume user sets env vars in Cloud Run deploy or secrets are pre-created.

# 4. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
# Note: DB connection string needs real values. 
# We use a placeholder or ask user to update revision later.
gcloud run deploy $APP_NAME \
    --image gcr.io/$PROJECT_ID/$APP_NAME \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars DB_TYPE=postgres \
    --set-env-vars DB_USER=postgres \
    --set-env-vars DB_HOST=localhost \
    --set-env-vars DB_PORT=5432 \
    --set-env-vars DB_NAME=dental_db \
    --set-env-vars ENCRYPTION_KEY="CHANGE_ME_IN_PRODUCTION"

echo "Deployment successful!"
echo "Next steps:"
echo "1. Create a Cloud SQL instance."
echo "2. Connect Cloud Run to Cloud SQL (add --add-cloudsql-instances flag)."
echo "3. Update ENCRYPTION_KEY and DB_PASSWORD using Secret Manager."
