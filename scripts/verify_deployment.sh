#!/bin/bash
# Verify Deployment Script
# Runs the end-to-end API test suite against the production environment.

set -e

# activate venv
source venv/bin/activate

echo "=================================================="
echo "🚀 Starting Deployment Verification"
echo "=================================================="
echo "Target: Production Cloud Run (US-CENTRAL1)"
echo "Tests:  tests/e2e/test_live_api.py"
echo "=================================================="

# Run the test suite
python tests/e2e/test_live_api.py

echo "=================================================="
echo "✅ Verification Complete"
echo "=================================================="
echo "Note: If Visits endpoint failed (500), ensure 'DELETED' enum migration is applied."
