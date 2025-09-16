#!/usr/bin/env bash
# Start script for API service on Render

set -e

echo "Starting API server..."

# Start the FastAPI application with Uvicorn
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers 1 \
    --log-level info