#!/bin/bash
set -e

# verify_gcp.sh
# Automated QA process for Dental Backend on GCP.
# Usage: ./scripts/verify_gcp.sh

echo "========================================================"
echo "Starting Automated QA on GCP"
echo "Target: Production (Live)"
echo "Timestamp: $(date)"
echo "========================================================"

# Ensure we are in the project root
cd "$(dirname "$0")/.."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment 'venv' not found."
    exit 1
fi

# Activate venv
source venv/bin/activate

# Install dependencies if needed (quietly)
pip install -q httpx

# Run the Python test suite
python3 tests/e2e/test_live_api.py

echo "========================================================"
echo "QA Process Complete"
echo "========================================================"
