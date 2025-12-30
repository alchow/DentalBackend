#!/bin/bash
# run_mcp.sh - Script to run the Dental Notes MCP Server

# 0. Ensure we are in the script's directory (Project Root)
cd "$(dirname "$0")"

# 1. Activate Virtual Environment if it exists
if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# 2. Check for Cloud SQL Proxy
# Redirect informational messages to stderr so they don't break JSON-RPC
echo "Starting Dental Notes MCP Server..." >&2
echo "Ensure DB env vars are set." >&2
# Debug: Print env vars to verify what Claude is passing
echo "DEBUG: DB_USER='$DB_USER'" >&2
echo "DEBUG: DB_HOST='$DB_HOST'" >&2
echo "DEBUG: DB_NAME='$DB_NAME'" >&2
# Do NOT print DB_PASS for security, but check if it exists
if [ -z "$DB_PASS" ]; then echo "DEBUG: DB_PASS is EMPTY" >&2; else echo "DEBUG: DB_PASS is SET" >&2; fi

# Default to local dev settings (Docker) if not set
export DB_HOST=${DB_HOST:-"127.0.0.1"}
# Change default to 'postgres' to match local docker-compose
export DB_USER=${DB_USER:-"postgres"}
export DB_NAME=${DB_NAME:-"dental_notes"} # Local DB name is dental_notes, Cloud is dental_db
export DB_PORT=${DB_PORT:-5432}

# Default password for local docker is usually 'postgres' or 'password'
if [ -z "$DB_PASS" ]; then
    export DB_PASS="postgres"
    echo "Using default local DB_PASS='postgres'. Export DB_PASS to override." >&2
fi

# 3. Run Server
# We use 'python3' and module path to ensure imports work
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend
exec python3 backend/app/mcp/server.py
