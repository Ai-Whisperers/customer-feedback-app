# Customer AI Driven Feedback Analyzer - Documentación

Sistema de análisis inteligente de comentarios de clientes mediante IA, diseñado para extraer insights valiosos de retroalimentación masiva con arquitectura escalable y modular.

## 📚 Índice de Documentación

### 🏗️ Arquitectura y Diseño
- [Arquitectura del Sistema](./arquitectura/sistema.md) - Visión general de la arquitectura monorepo
- [Flujo de Datos](./arquitectura/flujo-datos.md) - Pipeline de procesamiento end-to-end
- [Decisiones Técnicas](./arquitectura/decisiones-tecnicas.md) - Razonamiento detrás de las elecciones arquitectónicas

### 🔧 Guías de Implementación
- [Configuración Inicial](./guias/configuracion.md) - Setup del entorno de desarrollo
- [API Reference](./guias/api-reference.md) - Contratos y endpoints de la API
- [Integración OpenAI](./guias/openai-integration.md) - Uso de Responses API y Structured Outputs
- [Procesamiento Batch](./guias/batch-processing.md) - Sistema de chunking y paralelización

### 📊 Módulos de Análisis
- [Motor de Emociones](./modulos/emociones.md) - Sistema de detección de 16 emociones
- [Análisis NPS](./modulos/nps.md) - Cálculo y categorización Net Promoter Score
- [Predicción de Churn](./modulos/churn.md) - Modelo de riesgo de abandono
- [Extracción Pain Points](./modulos/pain-points.md) - Identificación de problemas recurrentes

### 🚀 Despliegue y Operaciones
- [Guía de Despliegue Render](./deployment/render.md) - Configuración de servicios en Render
- [Variables de Entorno](./deployment/variables.md) - Configuración de secrets y variables
- [Monitoreo y Logs](./deployment/monitoreo.md) - Observabilidad y debugging
- [Optimización de Costos](./deployment/costos.md) - Control de uso de API y recursos

### 📈 Visualización y Frontend
- [Componentes UI](./frontend/componentes.md) - Biblioteca de componentes React
- [Gráficas Plotly](./frontend/graficas.md) - Configuración y personalización de charts
- [Estado y Context](./frontend/estado.md) - Manejo de estado global con Context API
- [Diseño Responsive](./frontend/responsive.md) - Implementación con Tailwind CSS

### 🔒 Seguridad y Compliance
- [Validación de Datos](./seguridad/validacion.md) - Sanitización y límites
- [Manejo de Errores](./seguridad/errores.md) - Estrategias de recuperación
- [TTL y Limpieza](./seguridad/ttl.md) - Gestión de datos temporales
- [Rate Limiting](./seguridad/rate-limit.md) - Control de llamadas a API

### 🧪 Testing y Calidad
- [Estrategia de Testing](./testing/estrategia.md) - Niveles y tipos de tests
- [Tests de Integración](./testing/integracion.md) - Testing del pipeline completo
- [Benchmarks de Performance](./testing/performance.md) - Métricas y objetivos SLA
- [Validación de Outputs](./testing/validacion.md) - Aseguramiento de calidad de IA

### 📖 Guías de Usuario
- [Manual de Usuario](./usuario/manual.md) - Guía completa para usuarios finales
- [Interpretación de Resultados](./usuario/interpretacion.md) - Cómo leer los análisis
- [Casos de Uso](./usuario/casos-uso.md) - Ejemplos prácticos y escenarios
- [FAQ](./usuario/faq.md) - Preguntas frecuentes

## 🎯 Quick Start

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

## 🔑 Variables de Entorno Críticas

```env
OPENAI_API_KEY=sk-xxx
REDIS_URL=redis://localhost:6379
AI_MODEL=gpt-4o-mini
MAX_BATCH_SIZE=50
MAX_RPS=8
```

## 📐 Arquitectura Simplificada

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

## 📊 Capacidades del Sistema

- **Volumen**: 850-3000 comentarios por análisis
- **Velocidad**: <10s para 1200 comentarios
- **Idiomas**: Español e Inglés (detección automática)
- **Emociones**: 16 estados emocionales con probabilidades
- **Métricas**: NPS, Churn Risk, Pain Points
- **Formatos**: XLSX, XLS, CSV (entrada) | JSON, CSV, XLSX (salida)

## 🛠️ Stack Tecnológico

- **Frontend**: React 18 + TypeScript + Tailwind CSS + Plotly
- **Backend**: FastAPI + Celery + Pydantic
- **IA**: OpenAI Responses API + Structured Outputs
- **Infra**: Render.com + Redis (Upstash)
- **Observabilidad**: JSON Logging + Health Checks

## 📝 Contribución

Este proyecto sigue los principios de:
- Anti-overengineering
- Modularidad y predicción
- Archivos ≤250 líneas
- Entry points ≤150 líneas
- Documentación en español (pública)
- Comentarios/logs en inglés

## 🔗 Enlaces Importantes

- [OpenAI Responses API Docs](https://platform.openai.com/docs/api-reference/responses)
- [Render Documentation](https://docs.render.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)

---

**Versión**: 3.1.0
**Última actualización**: 2025-09-16
**Mantenedor**: Equipo de Ingeniería