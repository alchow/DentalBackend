#!/bin/bash
set -e

# Configuration
PROJECT_ID="dentaldb-482716"
REGION="us-central1"
SERVICE_NAME="dental-frontend"
REPO_NAME="dental-frontend-repo"
IMAGE_TAG="g-cr.io/$PROJECT_ID/$REPO_NAME/$SERVICE_NAME:latest"

# Backend URL (The Production Backend)
NEXT_PUBLIC_API_URL="https://dental-backend-963321342744.us-central1.run.app/api/v1"

echo "🚀 Deploying Frontend to GCP Cloud Run..."
echo "----------------------------------------"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "API URL: $NEXT_PUBLIC_API_URL"
echo "----------------------------------------"

# 1. Build & Push Container (using Cloud Build)
echo "📦 Building Container..."
# Note: We pass --build-arg if needed, but Next.js client-side vars are baked in at build time.
# We must ensure NEXT_PUBLIC_API_URL is available during the build.
gcloud builds submit frontend \
  --tag gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --project $PROJECT_ID

# 2. Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --project $PROJECT_ID \
  --allow-unauthenticated \
  --port 3000 \
  --set-env-vars NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

echo "✅ Deployment Complete!"
echo "You can access the frontend at the URL above."
