#!/usr/bin/env bash
# Build script for API service on Render

set -e

echo "Starting API build process..."

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

echo "API build completed successfully!"