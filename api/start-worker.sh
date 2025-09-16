#!/usr/bin/env bash
# Start script for Celery Worker service on Render
# Customer AI Driven Feedback Analyzer - Worker Start

set -e

echo "====================================="
echo "Starting Celery Worker..."
echo "====================================="

# Display environment info
echo "Python version: $(python --version)"
echo "Celery configuration:"
echo "  - Concurrency: ${CELERY_WORKER_CONCURRENCY:-2}"
echo "  - Log level: ${CELERY_LOG_LEVEL:-info}"
echo "  - Max tasks per child: ${CELERY_MAX_TASKS_PER_CHILD:-100}"

# Start Celery worker with proper configuration
celery -A app.workers.celery_app worker \
    --loglevel=${CELERY_LOG_LEVEL:-info} \
    --concurrency=${CELERY_WORKER_CONCURRENCY:-2} \
    --max-tasks-per-child=${CELERY_MAX_TASKS_PER_CHILD:-100} \
    --pool=prefork \
    --without-heartbeat \
    --without-gossip \
    --without-mingle