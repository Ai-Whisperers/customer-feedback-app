#!/usr/bin/env bash
# Build script for Web/BFF MPA service on Render
# Customer AI Driven Feedback Analyzer - Web Build v3.2.0

set -e

echo "====================================="
echo "Starting MPA Web/BFF build process..."
echo "====================================="

# Display Node version
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

# Display current location
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

# Clean all previous builds to prevent cache issues
echo "====================================="
echo "Cleaning previous builds..."
echo "====================================="
rm -rf dist client/dist node_modules/.vite 2>/dev/null || true
echo "Previous builds cleaned successfully"

# Install server dependencies
echo "====================================="
echo "Installing server dependencies..."
echo "====================================="
npm ci --production=false

# Build client application (MPA)
echo "====================================="
echo "Building client MPA application..."
echo "====================================="

cd client

# Install client dependencies
echo "Installing client dependencies..."
npm ci --production=false

# Build client with Vite (generates index.html, about.html, analyzer.html)
echo "Building client with Vite..."
npm run build

# Verify MPA build output
echo "Verifying MPA build output..."
if [ ! -f "dist/index.html" ]; then
    echo "ERROR: index.html not found in dist/"
    exit 1
fi
if [ ! -f "dist/about.html" ]; then
    echo "ERROR: about.html not found in dist/"
    exit 1
fi
if [ ! -f "dist/analyzer.html" ]; then
    echo "ERROR: analyzer.html not found in dist/"
    exit 1
fi

echo "MPA HTML files verified:"
ls -la dist/*.html

# Return to web directory
cd ..

# Compile TypeScript server
echo "====================================="
echo "Compiling TypeScript server..."
echo "====================================="
npx tsc -p tsconfig.server.json

# Verify server compilation
if [ ! -f "dist/server.js" ]; then
    echo "ERROR: server.js not compiled"
    exit 1
fi

# Copy client build to server dist
echo "====================================="
echo "Copying client build to server dist..."
echo "====================================="

# Use cross-platform copy command
if command -v cp &> /dev/null; then
    cp -r client/dist dist/client-build
else
    # Fallback for Windows
    xcopy /E /I /Y client\dist dist\client-build
fi

# Verify client files are copied
if [ ! -f "dist/client-build/index.html" ]; then
    echo "ERROR: Client files not copied correctly"
    exit 1
fi

# Validate build
echo "====================================="
echo "Validating build..."
echo "====================================="
npm run validate-build

# Display final structure
echo "====================================="
echo "Final build structure:"
echo "====================================="
echo "Server files:"
ls -la dist/ | head -10
echo ""
echo "Client files:"
ls -la dist/client-build/ | head -10
echo ""
echo "Asset files:"
ls -la dist/client-build/assets/ | head -10

echo "====================================="
echo "MPA Web/BFF build completed successfully!"
echo "Ready to serve:"
echo "  - / (Landing page)"
echo "  - /about (About page)"
echo "  - /analyzer (Analyzer page)"
echo "====================================="