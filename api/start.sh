#!/usr/bin/env bash
# Start script for API service on Render
# Customer AI Driven Feedback Analyzer - API Start

set -e

echo "====================================="
echo "Starting API server..."
echo "====================================="

# Display environment info
echo "Python version: $(python --version)"
echo "Environment configuration:"
echo "  - Port: ${PORT:-8000}"
echo "  - Workers: ${API_WORKERS:-1}"
echo "  - Log level: ${LOG_LEVEL:-info}"
echo "  - AI Model: ${AI_MODEL:-gpt-4o-mini}"
echo "  - Max batch size: ${MAX_BATCH_SIZE:-50}"
echo "  - Max RPS: ${MAX_RPS:-8}"

# Start the FastAPI application with Uvicorn
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers ${API_WORKERS:-1} \
    --log-level ${LOG_LEVEL:-info} \
    --access-log \
    --use-colors