#!/usr/bin/env bash
# Start script for Web/BFF service on Render
# Customer AI Driven Feedback Analyzer - Web Start

set -e

echo "====================================="
echo "Starting Web/BFF server..."
echo "====================================="

# Display environment info
echo "Node version: $(node --version)"
echo "Environment: ${NODE_ENV:-production}"
echo "Port: ${PORT:-3000}"
echo "API Proxy Target: ${API_PROXY_TARGET:-not set}"

# Navigate to web directory
cd web

# Start from the correct location
if [ -d "dist" ]; then
    echo "Starting from dist directory..."
    node dist/server.js
else
    echo "Warning: dist directory not found, starting development server..."
    node server/server.js
fi