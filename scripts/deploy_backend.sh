#!/bin/bash
set -e

# Configuration
PROJECT_ID="dentaldb-482716"
REGION="us-central1"
SERVICE_NAME="dental-backend"
CLOUD_SQL_INSTANCE="dentaldb-482716:us-central1:dentaldb"

echo "🚀 Deploying Backend to GCP Cloud Run..."
echo "----------------------------------------"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "----------------------------------------"

# Deploy from source with secrets, env vars, and Cloud SQL
echo "📦 Building Container..."
gcloud run deploy $SERVICE_NAME \
  --source backend \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --add-cloudsql-instances=$CLOUD_SQL_INSTANCE \
  --update-secrets="DB_PASS=DB_PASS:latest,SECRET_KEY=SECRET_KEY:latest,ENCRYPTION_KEY=ENCRYPTION_KEY:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,INTERNAL_API_KEY=INTERNAL_API_KEY:latest" \
  --update-env-vars="DB_TYPE=postgres,DB_USER=dental_user,DB_HOST=/cloudsql/$CLOUD_SQL_INSTANCE,DB_PORT=5432,DB_NAME=dental_db,CLOUD_TASKS_QUEUE=dental-summary-queue,CLOUD_TASKS_LOCATION=us-central1,SERVICE_ACCOUNT_EMAIL=963321342744-compute@developer.gserviceaccount.com,GCP_PROJECT=dentaldb-482716,SERVICE_URL=https://dental-backend-963321342744.us-central1.run.app"

echo "✅ Deployment Complete!"
