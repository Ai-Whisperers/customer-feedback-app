#!/usr/bin/env bash
# Build script for Web/BFF SPA service on Render
# Customer AI Driven Feedback Analyzer - Web Build v3.2.0

set -e

echo "====================================="
echo "Starting SPA Web/BFF build process..."
echo "====================================="

# Display Node version
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

# Display current location
echo "Current directory: $(pwd)"

# Navigate to project root for workspace installation
echo "====================================="
echo "Installing dependencies with workspaces..."
echo "====================================="
cd ..
npm ci --production=false
cd web

# Build client application (SPA)
echo "====================================="
echo "Building client SPA application..."
echo "====================================="
npm run build:client

# Build BFF server
echo "====================================="
echo "Building BFF server..."
echo "====================================="
npm run build:bff

# Verify SPA build output
echo "Verifying SPA build output..."
if [ ! -f "dist/client/index.html" ]; then
    echo "ERROR: index.html not found in dist/client/"
    exit 1
fi
if [ ! -d "dist/client/assets" ]; then
    echo "ERROR: assets directory not found in dist/client/"
    exit 1
fi

# Verify BFF build output
echo "Verifying BFF build output..."
if [ ! -f "dist/bff/server.js" ]; then
    echo "ERROR: server.js not found in dist/bff/"
    exit 1
fi

echo "SPA build files verified:"
echo "  - index.html (main entry point)"
echo "  - assets/ directory with JS/CSS bundles"
echo "  - BFF server compiled"

# Display final structure
echo "====================================="
echo "Final build structure:"
echo "====================================="
echo "BFF files:"
ls -la dist/bff/ | head -10
echo ""
echo "Client files:"
ls -la dist/client/ | head -10

echo "====================================="
echo "SPA Web/BFF build completed successfully!"
echo "Ready to serve:"
echo "  - /* → index.html (SPA with React Router)"
echo "    - / (Landing page)"
echo "    - /about (About page)"
echo "    - /analyzer (Analyzer page)"
echo "====================================="