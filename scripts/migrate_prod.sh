#!/bin/bash
set -e
trap "kill 0" EXIT

# scripts/migrate_prod.sh
# Connects to Production Cloud SQL via Proxy and runs Alembic Migrations.

CONNECTION_NAME="dentaldb-482716:us-central1:dentaldb"
PROXY_PORT=5434

echo "========================================================"
echo "PRODUCTION DB MIGRATION"
echo "Target: $CONNECTION_NAME"
echo "========================================================"

# 1. Fetch Secret
echo "🔐 Fetching DB_PASS from Secret Manager..."
export DB_PASS=$(gcloud secrets versions access latest --secret="DB_PASS" --project=dentaldb-482716)

if [ -z "$DB_PASS" ]; then
    echo "❌ Failed to fetch DB_PASS"
    exit 1
fi

# 2. Start Proxy (from project root where cloud_sql_proxy lives)
echo "🔌 Starting Cloud SQL Proxy on port $PROXY_PORT..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

./cloud_sql_proxy -instances=$CONNECTION_NAME=tcp:$PROXY_PORT &
PROXY_PID=$!
echo "   PID: $PROXY_PID"

# Give it a moment to connect
sleep 3

# 3. Monitor Proxy (Optional check if still running)
if ! ps -p $PROXY_PID > /dev/null; then
   echo "❌ Proxy failed to start"
   exit 1
fi

# 4. Run Migration
echo "🚀 Running Alembic Upgrade..."
cd backend
export DB_HOST=127.0.0.1
export DB_PORT=$PROXY_PORT
export DB_USER=dental_user
export DB_NAME=dental_db
# DB_PASS is already exported

# Ensure venv is active
source venv/bin/activate

alembic upgrade head

MIG_EXIT_CODE=$?

# 5. Cleanup
echo "🧹 Stopping Proxy..."
kill $PROXY_PID

if [ $MIG_EXIT_CODE -eq 0 ]; then
    echo "✅ Migration Successful"
else
    echo "❌ Migration Failed"
    exit $MIG_EXIT_CODE
fi
