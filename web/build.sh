#!/usr/bin/env bash
# Build script for Web/BFF service on Render
# Customer AI Driven Feedback Analyzer - Web Build

set -e

echo "====================================="
echo "Starting Web/BFF build process..."
echo "====================================="

# Display Node version
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

# Navigate to web directory
cd web

# Install root dependencies
echo "Installing root dependencies..."
npm ci --production=false

# Build client application
echo "Building client application..."

# Navigate to client directory
cd client

# Install client dependencies with all devDependencies
echo "Installing client dependencies..."
npm ci --production=false

# Build client
echo "Running client build..."
npm run build

# Return to web directory
cd ..

# Compile TypeScript server
echo "Compiling TypeScript server..."
npx tsc server/server.ts \
    --outDir dist \
    --esModuleInterop \
    --module commonjs \
    --target es2020 \
    --resolveJsonModule \
    --skipLibCheck

# Copy client build to dist
echo "Copying client build to dist..."
cp -r client/dist dist/client-build

# Create production package.json for server
cat > dist/package.json << 'EOF'
{
  "name": "feedback-analyzer-server",
  "version": "3.1.0",
  "main": "server.js",
  "dependencies": {
    "express": "^4.21.1",
    "http-proxy-middleware": "^3.0.3",
    "compression": "^1.7.4",
    "helmet": "^8.0.0",
    "dotenv": "^16.4.5"
  }
}
EOF

# Install production dependencies in dist
echo "Installing production dependencies..."
npm ci --production --prefix dist

echo "====================================="
echo "Web/BFF build completed successfully!"
echo "Build output in: dist/"
echo "====================================="