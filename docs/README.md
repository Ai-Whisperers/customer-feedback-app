# Customer AI Driven Feedback Analyzer - Documentación

Sistema de análisis inteligente de comentarios de clientes mediante IA, diseñado para extraer insights valiosos de retroalimentación masiva con arquitectura escalable y modular.

**Versión:** 3.2.0
**Estado:** Producción
**Última actualización:** Septiembre 2024

## Índice de Documentación

### Documentación Principal
- [Documentación Técnica Completa](./TECHNICAL_DOCUMENTATION.md) - Arquitectura, API, optimizaciones y deployment
- [Arquitectura Frontend](./FRONTEND_ARCHITECTURE.md) - Estructura modular, componentes y optimizaciones
- [Guía de Deployment en Render](./RENDER_DEPLOYMENT.md) - Configuración de servicios y variables de entorno
- [Integración de Servicios](./SERVICE_INTEGRATION.md) - Comunicación entre web, API y worker
- [CI/CD](./CICD.md) - Pipeline de integración continua
- [Reglas del Proyecto](./PROJECT_RULES.md) - Convenciones y estándares de código

### Guías Específicas

#### Arquitectura
- [Sistema General](./arquitectura/sistema.md) - Visión general de la arquitectura monorepo
- [Flujo de Datos](./arquitectura/flujo-datos.md) - Pipeline de procesamiento end-to-end

#### Implementación
- [API Reference](./guias/api-reference.md) - Endpoints y contratos de la API
- [Integración OpenAI](./guias/openai-integration.md) - Uso de API y Structured Outputs

#### Módulos de Análisis
- [Motor de Emociones](./modulos/emociones.md) - Sistema de detección de 7 emociones

#### Deployment
- [Render.com](./deployment/render.md) - Configuración detallada de servicios en Render

## Quick Start

```bash
# 1. Clonar repositorio
git clone <repository-url>
cd customer-feedback-app

# 2. Instalar dependencias
cd web && npm install
cd ../api && pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 4. Iniciar servicios locales
# Terminal 1: API
cd api && uvicorn app.main:app --reload

# Terminal 2: Worker
cd api && celery -A app.workers.celery_app worker --loglevel=INFO

# Terminal 3: Frontend
cd web && npm run dev
```

## Variables de Entorno Críticas

```env
OPENAI_API_KEY=sk-xxx
REDIS_URL=redis://localhost:6379
AI_MODEL=gpt-4o-mini
MAX_BATCH_SIZE=50
MAX_RPS=8
```

## Arquitectura Simplificada

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│  Web (BFF)  │────▶│  API (priv) │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                     │
                           │                     ▼
                           │              ┌─────────────┐
                           └─────────────▶│    Redis    │
                                          └─────────────┘
                                                 ▲
                                                 │
                                          ┌─────────────┐
                                          │   Worker    │
                                          └─────────────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │  OpenAI API │
                                          └─────────────┘
```

## Capacidades del Sistema

- **Volumen**: 100-3000 comentarios por análisis
- **Velocidad**: ~3s para 100 comentarios, ~30s para 3000 comentarios
- **Idiomas**: Español e Inglés (detección automática)
- **Emociones**: 7 estados emocionales con probabilidades (Satisfacción, Frustración, Enojo, Confianza, Decepción, Confusión, Anticipación)
- **Métricas**: NPS, Churn Risk (0-1), Pain Points (hasta 5 por comentario), Sentiment Score (-1 a 1)
- **Formatos**: XLSX, XLS, CSV (entrada) | JSON, CSV, XLSX (salida con formato profesional)

## Stack Tecnológico

- **Frontend**: React 18.3 + TypeScript 5.6 + Tailwind CSS 3.4 + Plotly.js + Vite 5.4
- **Backend**: FastAPI 0.115 + Python 3.11+ + Pydantic 2.9
- **Workers**: Celery 5.4 con 4 workers concurrentes
- **IA**: OpenAI GPT-4o-mini + VADER Sentiment + TextBlob (análisis híbrido)
- **Cache/Queue**: Redis 7.0+ (24h TTL para resultados)
- **Infra**: Render.com (4 servicios: web, api, worker, redis)
- **Observabilidad**: Structlog + Health Checks + Métricas de performance

## Contribución

Este proyecto sigue los principios de:
- Anti-overengineering
- Modularidad y predicción
- Archivos ≤250 líneas
- Entry points ≤150 líneas
- Documentación en español (pública)
- Comentarios/logs en inglés

## Enlaces Importantes

- [OpenAI Responses API Docs](https://platform.openai.com/docs/api-reference/responses)
- [Render Documentation](https://docs.render.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)

---

**Versión**: 3.2.0
**Última actualización**: Septiembre 2024
**Mantenido por**: AI Whisperers Team