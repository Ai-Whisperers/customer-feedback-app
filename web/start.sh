#!/usr/bin/env bash
# Start script for Web/BFF MPA service on Render
# Customer AI Driven Feedback Analyzer - Web Start v3.2.0

set -e

echo "====================================="
echo "Starting MPA Web/BFF server..."
echo "====================================="

# Display environment info
echo "Node version: $(node --version)"
echo "Environment: ${NODE_ENV:-production}"
echo "Port: ${PORT:-3000}"
echo "API Proxy Target: ${API_PROXY_TARGET:-not set}"
echo "Current directory: $(pwd)"

# Verify we have the built files
if [ ! -f "dist/server.js" ]; then
    echo "ERROR: dist/server.js not found!"
    echo "Build may have failed. Contents of dist:"
    ls -la dist/ 2>/dev/null || echo "dist directory not found"
    exit 1
fi

if [ ! -d "dist/client-build" ]; then
    echo "ERROR: dist/client-build directory not found!"
    echo "Client build may have failed."
    exit 1
fi

# Verify MPA HTML files exist
echo "====================================="
echo "Verifying MPA files..."
echo "====================================="

if [ ! -f "dist/client-build/index.html" ]; then
    echo "ERROR: index.html not found in dist/client-build/"
    exit 1
fi

if [ ! -f "dist/client-build/about.html" ]; then
    echo "ERROR: about.html not found in dist/client-build/"
    exit 1
fi

if [ ! -f "dist/client-build/analyzer.html" ]; then
    echo "ERROR: analyzer.html not found in dist/client-build/"
    exit 1
fi

echo "✓ All MPA HTML files verified"
echo "  - index.html (Landing)"
echo "  - about.html (About)"
echo "  - analyzer.html (Analyzer)"

# Display what we're serving
echo "====================================="
echo "Server configuration:"
echo "====================================="
echo "Static files from: dist/client-build/"
echo "MPA Routes:"
echo "  GET / → index.html"
echo "  GET /about → about.html"
echo "  GET /analyzer → analyzer.html"
echo "  GET /api/* → Proxy to ${API_PROXY_TARGET}"
echo "====================================="

# Start the Express server
echo "Starting Express server..."
exec node dist/server.js