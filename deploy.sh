#!/bin/bash
set -e

APP_NAME="dental-backend"
REGION="us-central1"
# Check for gcloud
GCLOUD_BIN_DIR="/Users/albert/Projects/google-cloud-sdk/bin"
if [ -d "$GCLOUD_BIN_DIR" ]; then
    export PATH="$GCLOUD_BIN_DIR:$PATH"
else
    echo "Error: gcloud bin directory not found at $GCLOUD_BIN_DIR"
    exit 1
fi

APP_NAME="dental-backend"
REGION="us-central1"
PROJECT_ID="dentaldb-482716" # Hardcoded correct project ID

# if [ -z "$PROJECT_ID" ]; then
#     echo "Error: behaviors Cloud SDK project not set."
#     echo "Run 'gcloud config set project <PROJECT_ID>' first."
#     exit 1
# fi

echo "Deploying $APP_NAME to project $PROJECT_ID in $REGION..."

# Generate Secrets if not provided
SECRET_KEY=$(openssl rand -hex 32)
# Generate a valid Fernet key (requires cryptography or manual base64 encoding of 32 random bytes)
# We can use python for this if available, or openssl + base64
if command -v python3 &> /dev/null; then
    ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
else
    # Fallback to OpenSSL (32 bytes -> base64)
    ENCRYPTION_KEY=$(openssl rand -base64 32)
fi

echo "Generated temporary SECRET_KEY and ENCRYPTION_KEY for deployment."

# 1. Enable APIs (Skipping to avoid permission errors if already enabled)
# echo "Enabling necessary APIs..."
# gcloud services enable run.googleapis.com \
#                        sqladmin.googleapis.com \
#                        secretmanager.googleapis.com \
#                        artifactregistry.googleapis.com

# 2. Build and Push (using Cloud Build for simplicity)
echo "Building container image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$APP_NAME . --project $PROJECT_ID

# 3. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $APP_NAME \
    --image gcr.io/$PROJECT_ID/$APP_NAME \
    --project $PROJECT_ID \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --set-env-vars DB_TYPE=postgres \
    --set-env-vars DB_USER=postgres \
    --set-env-vars DB_HOST=localhost \
    --set-env-vars DB_PORT=5432 \
    --set-env-vars DB_NAME=dental_db \
    --set-env-vars ENCRYPTION_KEY="$ENCRYPTION_KEY" \
    --set-env-vars SECRET_KEY="$SECRET_KEY"

echo "Deployment successful!"
echo "Next steps:"
echo "1. Create a Cloud SQL instance."
echo "2. Connect Cloud Run to Cloud SQL (add --add-cloudsql-instances flag)."
echo "3. Update ENCRYPTION_KEY and DB_PASSWORD using Secret Manager."
