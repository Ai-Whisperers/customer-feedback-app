#!/usr/bin/env bash
# Build script for Celery Worker service on Render
# Customer AI Driven Feedback Analyzer - Worker Build

set -e

echo "====================================="
echo "Starting Worker build process..."
echo "====================================="

# Display Python version
python --version

# Upgrade pip to latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Verify critical dependencies
echo "Verifying critical dependencies..."
python -c "import celery; print(f'Celery version: {celery.__version__}')"
python -c "import redis; print(f'Redis version: {redis.__version__}')"
python -c "import openai; print(f'OpenAI version: {openai.__version__}')"
python -c "import pandas; print(f'Pandas version: {pandas.__version__}')"

echo "====================================="
echo "Worker build completed successfully!"
echo "====================================="