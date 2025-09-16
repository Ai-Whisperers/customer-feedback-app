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

# Ensure we're in the correct directory
if [ -d "dist" ]; then
    echo "Starting from dist directory..."
    cd dist
    node server.js
else
    echo "Warning: dist directory not found, starting development server..."
    node server/server.js
fi