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

echo -e "\n${YELLOW}5. Verificando archivos duplicados eliminados...${NC}"
if [ -f "web/client/src/components/FileUpload.tsx" ]; then
    echo -e "${RED}ERROR: FileUpload.tsx duplicado aún existe${NC}"
else
    echo -e "${GREEN}OK: FileUpload.tsx duplicado eliminado${NC}"
fi

if [ -f "web/client/src/components/ProgressTracker.tsx" ]; then
    echo -e "${RED}ERROR: ProgressTracker.tsx duplicado aún existe${NC}"
else
    echo -e "${GREEN}OK: ProgressTracker.tsx duplicado eliminado${NC}"
fi

echo -e "\n${YELLOW}6. Verificando imports corregidos...${NC}"
grep "@/components/upload/FileUpload" web/client/src/pages/AnalyzerPage.tsx > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}OK: Import de FileUpload actualizado${NC}"
else
    echo -e "${RED}ERROR: Import de FileUpload no actualizado${NC}"
fi

grep "@/components/progress/ProgressTracker" web/client/src/pages/AnalyzerPage.tsx > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}OK: Import de ProgressTracker actualizado${NC}"
else
    echo -e "${RED}ERROR: Import de ProgressTracker no actualizado${NC}"
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
