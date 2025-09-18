#!/bin/bash
# Script de verificación post-deploy
# Customer Feedback Analyzer - Deploy Verification

echo "======================================"
echo "VERIFICACIÓN DE DEPLOYMENT"
echo "======================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "\n${YELLOW}1. Verificando servicios en Render...${NC}"
./tools/render_cli_v2.1.4.exe services list --output json | grep -E "(customer-feedback|celery-worker)" | head -10

echo -e "\n${YELLOW}2. Testing health endpoints...${NC}"
echo "Testing frontend health..."
curl -s -o /dev/null -w "%{http_code}" https://customer-feedback-app.onrender.com/health
echo ""

echo "Testing API proxy..."
curl -s -o /dev/null -w "%{http_code}" https://customer-feedback-app.onrender.com/api/health
echo ""

echo -e "\n${YELLOW}3. Verificando versiones Python...${NC}"
echo "render.yaml version:"
grep "PYTHON_VERSION" render.yaml | head -1
echo "runtime.txt version:"
cat runtime.txt

echo -e "\n${YELLOW}4. Verificando OpenAI version...${NC}"
grep "openai==" api/requirements.txt

echo -e "\n${YELLOW}5. Verificando arquitectura SPA...${NC}"
if [ -f "web/client/about.html" ]; then
    echo -e "${RED}ERROR: about.html MPA file still exists${NC}"
else
    echo -e "${GREEN}OK: about.html MPA file removed${NC}"
fi

if [ -f "web/client/analyzer.html" ]; then
    echo -e "${RED}ERROR: analyzer.html MPA file still exists${NC}"
else
    echo -e "${GREEN}OK: analyzer.html MPA file removed${NC}"
fi

if [ -f "web/client/src/main.tsx" ]; then
    echo -e "${GREEN}OK: main.tsx SPA entrypoint exists${NC}"
else
    echo -e "${RED}ERROR: main.tsx SPA entrypoint missing${NC}"
fi

if [ -f "web/client/src/App.tsx" ]; then
    echo -e "${GREEN}OK: App.tsx with React Router exists${NC}"
else
    echo -e "${RED}ERROR: App.tsx with React Router missing${NC}"
fi

echo -e "\n${YELLOW}6. Verificando estructuras consolidadas...${NC}"
if [ -d "web/client/src/lib" ]; then
    echo -e "${RED}ERROR: lib/ directory still exists (should be consolidated into utils/)${NC}"
else
    echo -e "${GREEN}OK: lib/ directory removed and consolidated into utils/${NC}"
fi

if [ -d "web/client/src/utils/api" ]; then
    echo -e "${GREEN}OK: API utilities consolidated in utils/api/${NC}"
else
    echo -e "${RED}ERROR: API utilities not found in utils/api/${NC}"
fi

echo -e "\n======================================"
echo -e "${GREEN}VERIFICACIÓN COMPLETADA${NC}"
echo "======================================"
echo ""
echo "Próximos pasos:"
echo "1. Commit y push de cambios:"
echo "   git add -A"
echo "   git commit -m 'fix: Resolve deployment issues - Python version, OpenAI client, and frontend duplicates'"
echo "   git push origin main"
echo ""
echo "2. Monitorear deploys en Render dashboard"
echo "3. Verificar logs de servicios:"
echo "   ./tools/render_cli_v2.1.4.exe logs customer-feedback-api --tail"
echo "   ./tools/render_cli_v2.1.4.exe logs celery-worker --tail"
echo "4. Verificar SPA functionality:"
echo "   https://customer-feedback-app.onrender.com/ (Landing)"
echo "   https://customer-feedback-app.onrender.com/about (About - React Router)"
echo "   https://customer-feedback-app.onrender.com/analyzer (Analyzer - React Router)"
