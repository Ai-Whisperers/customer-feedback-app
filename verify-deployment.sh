#!/usr/bin/env bash
# Deployment verification script for Customer AI Driven Feedback Analyzer
# This script verifies that all necessary files and configurations are in place

set -e

echo "====================================="
echo "Deployment Verification Script"
echo "Customer AI Driven Feedback Analyzer"
echo "====================================="
echo ""

ERRORS=0
WARNINGS=0

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo "[OK] $1"
    else
        echo "[ERROR] Missing: $1"
        ERRORS=$((ERRORS + 1))
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo "[OK] Directory: $1"
    else
        echo "[ERROR] Missing directory: $1"
        ERRORS=$((ERRORS + 1))
    fi
}

echo "1. Checking root configuration files..."
echo "----------------------------------------"
check_file "render.yaml"
check_file ".gitignore"
check_file "README.md"
echo ""

echo "2. Checking API service files..."
echo "---------------------------------"
check_dir "api"
check_file "api/requirements.txt"
check_file "api/build.sh"
check_file "api/start.sh"
check_file "api/build-worker.sh"
check_file "api/start-worker.sh"
check_dir "api/app"
check_file "api/app/main.py"
check_dir "api/app/workers"
check_file "api/app/workers/celery_app.py"
echo ""

echo "3. Checking Web service files..."
echo "---------------------------------"
check_dir "web"
check_file "web/package.json"
check_file "web/build.sh"
check_file "web/start.sh"
check_dir "web/server"
check_file "web/server/server.ts"
check_dir "web/client"
check_file "web/client/package.json"
check_dir "web/client/src"
echo ""

echo "4. Verifying Python dependencies..."
echo "------------------------------------"
cd api
if python -c "import pkg_resources; pkg_resources.require(open('requirements.txt').read())" 2>/dev/null; then
    echo "[INFO] Python dependencies check skipped (install required)"
else
    echo "[INFO] Python dependencies need to be installed"
fi
cd ..
echo ""

echo "5. Verifying Node.js configuration..."
echo "--------------------------------------"
if [ -f "web/package.json" ]; then
    cd web
    if command -v node &> /dev/null; then
        echo "[OK] Node.js is installed: $(node --version)"
    else
        echo "[WARNING] Node.js not found"
        WARNINGS=$((WARNINGS + 1))
    fi

    if command -v npm &> /dev/null; then
        echo "[OK] NPM is installed: $(npm --version)"
    else
        echo "[WARNING] NPM not found"
        WARNINGS=$((WARNINGS + 1))
    fi
    cd ..
fi
echo ""

echo "6. Checking environment variables in render.yaml..."
echo "---------------------------------------------------"
if grep -q "OPENAI_API_KEY" render.yaml; then
    echo "[OK] OPENAI_API_KEY configured"
else
    echo "[ERROR] OPENAI_API_KEY not found in render.yaml"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "REDIS_URL" render.yaml; then
    echo "[OK] REDIS_URL configured"
else
    echo "[ERROR] REDIS_URL not found in render.yaml"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "API_PROXY_TARGET" render.yaml; then
    echo "[OK] API_PROXY_TARGET configured"
else
    echo "[ERROR] API_PROXY_TARGET not found in render.yaml"
    ERRORS=$((ERRORS + 1))
fi
echo ""

echo "7. Checking build commands..."
echo "------------------------------"
echo "Verifying API build command..."
if grep -q "buildCommand: cd api && bash build.sh" render.yaml; then
    echo "[OK] API build command configured"
else
    echo "[WARNING] API build command may need adjustment"
    WARNINGS=$((WARNINGS + 1))
fi

echo "Verifying Worker build command..."
if grep -q "buildCommand: cd api && bash build-worker.sh" render.yaml; then
    echo "[OK] Worker build command configured"
else
    echo "[WARNING] Worker build command may need adjustment"
    WARNINGS=$((WARNINGS + 1))
fi

echo "Verifying Web build command..."
if grep -q "buildCommand: cd web && bash build.sh" render.yaml; then
    echo "[OK] Web build command configured"
else
    echo "[WARNING] Web build command may need adjustment"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

echo "====================================="
echo "Verification Summary"
echo "====================================="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo "SUCCESS: All checks passed! Ready for deployment."
    else
        echo "SUCCESS with warnings: The application should deploy, but review warnings above."
    fi
    exit 0
else
    echo "FAILURE: There are $ERRORS error(s) that must be fixed before deployment."
    exit 1
fi