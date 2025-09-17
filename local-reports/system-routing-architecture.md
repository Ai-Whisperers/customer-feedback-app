# Reporte de Arquitectura y Enrutamiento del Sistema
**Fecha:** 2024-09-17
**Versión del Sistema:** 3.1.0
**Estado:** Producción en Render.com

## 1. Resumen Ejecutivo

Este documento detalla la arquitectura de enrutamiento del sistema Customer AI Driven Feedback Analyzer, identificando los nodos críticos, flujos de datos y puntos de falla potenciales en la infraestructura desplegada en Render.com.

## 2. Arquitectura General del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        INTERNET                              │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   RENDER CDN / EDGE                          │
│                    (Static Assets)                           │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              WEB SERVICE (Node.js + React)                   │
│                   PUBLIC - Port 3000                         │
│                 [NODO CRÍTICO NIVEL 1]                       │
│                                                              │
│  Rutas Frontend (React Router):                             │
│  • / → LandingPage                                          │
│  • /analyzer → AnalyzerPage                                 │
│  • /about → AboutPage                                       │
│                                                              │
│  Proxy Routes (BFF):                                        │
│  • /api/* → FastAPI Backend                                 │
└─────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │   Internal Network   │
                    └──────────┬──────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                API SERVICE (FastAPI)                         │
│                  PRIVATE - Port 8000                         │
│                [NODO CRÍTICO NIVEL 1]                        │
│                                                              │
│  Endpoints:                                                  │
│  • POST /api/upload → File upload & validation              │
│  • GET /api/status/{task_id} → Task status                  │
│  • GET /api/results/{task_id} → Analysis results            │
│  • GET /api/export/{task_id} → Export CSV/XLSX              │
│  • GET /health → Health check                               │
└─────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │    Message Queue     │
                    └──────────┬──────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               WORKER SERVICE (Celery)                        │
│                  PRIVATE - No Port                           │
│                [NODO CRÍTICO NIVEL 2]                        │
│                                                              │
│  Tasks:                                                      │
│  • process_feedback_task → Main processing                  │
│  • batch_processor → Batch analysis                         │
│  • openai_analyzer → AI integration                         │
└─────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │   External Services  │
                    └──────────┬──────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                         │
│                                                              │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │   Redis/Upstash   │        │   OpenAI API     │          │
│  │ [NODO CRÍTICO L1] │        │ [NODO CRÍTICO L1] │          │
│  │  - Message Broker │        │  - GPT-4o-mini   │          │
│  │  - Result Backend │        │  - Rate Limited   │          │
│  │  - Cache (24h TTL)│        │  - 8 RPS Max     │          │
│  └──────────────────┘        └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 3. Flujos de Enrutamiento Detallados

### 3.1 Flujo de Usuario Web (MPA - Multiple Page Application)

```
Usuario → Browser → Render CDN
                     ↓
              Web Service (Node.js)
                     ↓
            React Router Resolution
                     ↓
        ┌────────────┼────────────┐
        │            │            │
   LandingPage  AnalyzerPage  AboutPage
        │            │            │
        └────────────┼────────────┘
                     ↓
              Component Render
```

**Rutas del Frontend:**
- `/` - Landing page (default) - Página de inicio con glassmorphism
- `/analyzer` - Aplicación principal de análisis
- `/about` - Información del proyecto
- Todas las rutas no definidas → Redirect a `/`

### 3.2 Flujo de API (Backend for Frontend Pattern)

```
React App → Axios Request → /api/*
                ↓
        Web Service (BFF Proxy)
                ↓
    http-proxy-middleware (Node.js)
                ↓
    Private API Service (FastAPI)
                ↓
        Route Processing
                ↓
    ┌───────────┼───────────┐
    │           │           │
  Upload    Status      Results
    │           │           │
    └───────────┼───────────┘
                ↓
         Celery Task Queue
```

**Configuración del Proxy BFF:**
```javascript
// server/server.ts
app.use('/api', createProxyMiddleware({
  target: process.env.API_PROXY_TARGET,
  changeOrigin: true,
  pathRewrite: { '^/api': '/api' },
  timeout: 120000,
  proxyTimeout: 120000
}));
```

### 3.3 Flujo de Procesamiento Asíncrono

```
FastAPI → Celery Task Creation
            ↓
      Redis Queue (Broker)
            ↓
    Celery Worker Pickup
            ↓
    Batch Processing Loop
            ↓
    OpenAI API Calls (Parallel)
            ↓
    Redis Result Storage
            ↓
    Status Update in Redis
```

## 4. Nodos Críticos del Sistema

### 4.1 Nodos Críticos Nivel 1 (Falla Total del Sistema)

| Nodo | Servicio | Impacto de Falla | Mitigación Actual |
|------|----------|------------------|-------------------|
| Web Service | Node.js + Express | Sistema completamente inaccesible | Render auto-restart, health checks |
| API Service | FastAPI | No hay procesamiento posible | Render auto-restart, /health endpoint |
| Redis | Upstash/External | No hay comunicación entre servicios | Persistencia externa, backups |
| OpenAI API | GPT-4o-mini | No hay análisis de texto | Rate limiting, retry logic |

### 4.2 Nodos Críticos Nivel 2 (Degradación del Servicio)

| Nodo | Servicio | Impacto de Falla | Mitigación Actual |
|------|----------|------------------|-------------------|
| Worker Service | Celery | Tareas en cola sin procesar | Auto-scaling, múltiples workers |
| CDN | Render Static | Assets lentos de cargar | Cache browser, service worker |
| Database Results | Redis TTL | Resultados expiran en 24h | Exportación inmediata disponible |

## 5. Puntos de Enrutamiento Críticos

### 5.1 Frontend Routing (React Router v6)

```typescript
// web/src/App.tsx
<Router>
  <Routes>
    <Route path="/" element={<LandingPage />} />
    <Route path="/about" element={<AboutPage />} />
    <Route path="/analyzer" element={<AnalyzerPage />} />
  </Routes>
</Router>
```

**Consideraciones:**
- No hay rutas protegidas (no auth required)
- No hay lazy loading implementado
- Todas las rutas son públicas
- No hay middleware de navegación

### 5.2 API Routing (FastAPI)

```python
# api/app/main.py
app.include_router(upload.router, prefix="/api")
app.include_router(status.router, prefix="/api")
app.include_router(results.router, prefix="/api")
app.include_router(export.router, prefix="/api")
```

**Endpoints Críticos:**
- `POST /api/upload` - Entrada principal del sistema
- `GET /api/status/{task_id}` - Polling continuo (2s intervals)
- `GET /api/results/{task_id}` - Descarga de resultados grandes

### 5.3 Task Routing (Celery)

```python
# api/app/workers/celery_app.py
@celery_app.task(name="process_feedback")
def process_feedback_task(file_data, task_id):
    # Procesamiento en batches de 50-100 rows
    # Máximo 8 RPS a OpenAI
```

## 6. Configuración de Red y Seguridad

### 6.1 Topología de Red en Render

```
Internet → Public Web Service
              ↓
    Private Network (10.x.x.x)
              ↓
    ┌─────────┴─────────┐
    │                   │
API Service      Worker Service
    │                   │
    └─────────┬─────────┘
              ↓
      External Redis (TLS)
```

### 6.2 Políticas de Seguridad

| Capa | Configuración | Propósito |
|------|--------------|-----------|
| Web | Helmet.js | Headers de seguridad HTTP |
| Web | CORS disabled | Evita problemas cross-origin |
| API | Private service | No accesible desde internet |
| Worker | Private service | No accesible desde internet |
| Redis | TLS connection | Encriptación en tránsito |
| OpenAI | API Key en env | Secretos seguros |

## 7. Métricas de Performance y Límites

### 7.1 Límites del Sistema

| Componente | Límite | Configuración |
|------------|--------|---------------|
| File Upload | 20MB | `FILE_MAX_MB=20` |
| Batch Size | 100 rows | `MAX_BATCH_SIZE=100` |
| OpenAI RPS | 8 calls/sec | `MAX_RPS=8` |
| Results TTL | 24 hours | `RESULTS_TTL_SECONDS=86400` |
| Request Timeout | 120 seconds | Proxy timeout config |
| Worker Concurrency | 4 | Celery worker config |

### 7.2 Performance Esperado

| Volumen de Datos | Tiempo de Procesamiento | Throughput |
|------------------|------------------------|------------|
| 850-1200 rows | 5-10 segundos | ~150 rows/sec |
| 1800 rows | ~18 segundos | ~100 rows/sec |
| 3000 rows | ~30 segundos | ~100 rows/sec |

## 8. Monitoreo y Observabilidad

### 8.1 Health Checks

```python
# API Health Check
GET /health → {
  "status": "healthy",
  "redis": "connected",
  "worker": "active"
}
```

### 8.2 Logs Críticos

| Servicio | Log Location | Información Clave |
|----------|--------------|-------------------|
| Web | stdout | Proxy requests, errors |
| API | stdout | Request/response, validation |
| Worker | stdout | Task execution, OpenAI calls |
| Redis | Upstash console | Connection stats, memory |

## 9. Plan de Recuperación ante Fallos

### 9.1 Escenarios de Falla y Respuesta

| Escenario | Detección | Acción Automática | Acción Manual |
|-----------|-----------|-------------------|---------------|
| Web service down | Render health check | Auto-restart | Check logs, redeploy |
| API service down | Render health check | Auto-restart | Check dependencies |
| Worker crash | Task timeout | Celery retry | Scale workers, check memory |
| Redis down | Connection error | Retry connection | Check Redis provider |
| OpenAI API down | HTTP 503 | Exponential backoff | Switch to fallback model |

### 9.2 Procedimiento de Rollback

1. **Identificar versión estable anterior:**
   ```bash
   git log --oneline -10
   ```

2. **Rollback en Render:**
   - Web Service → Settings → Deploy specific commit
   - API Service → Settings → Deploy specific commit
   - Worker Service → Settings → Deploy specific commit

3. **Verificar servicios:**
   ```bash
   curl https://[web-url]/health
   curl https://[web-url]/api/health
   ```

## 10. Optimizaciones Recomendadas

### 10.1 Corto Plazo (Sprint actual)
- [ ] Implementar circuit breaker para OpenAI API
- [ ] Agregar cache de resultados procesados
- [ ] Implementar retry automático en frontend

### 10.2 Mediano Plazo (Próximo mes)
- [ ] Migrar a PostgreSQL para metadata
- [ ] Implementar WebSockets para status real-time
- [ ] Agregar CDN para assets estáticos

### 10.3 Largo Plazo (Próximo quarter)
- [ ] Implementar auto-scaling horizontal
- [ ] Agregar redundancia geográfica
- [ ] Implementar API Gateway pattern

## 11. Conclusiones

El sistema actual presenta una arquitectura robusta con separación clara de responsabilidades mediante el patrón BFF y procesamiento asíncrono. Los nodos críticos principales son:

1. **Web Service (BFF)** - Punto único de entrada
2. **Redis** - Comunicación inter-servicios
3. **OpenAI API** - Core del análisis

La arquitectura MPA con React Router permite navegación fluida entre páginas manteniendo el estado de la aplicación. El uso de glassmorphism y Tailwind CSS proporciona una experiencia de usuario moderna y consistente.

### Riesgos Principales:
- Dependencia total de Redis (single point of failure)
- Sin fallback si OpenAI API falla
- No hay persistencia de resultados más allá de 24h

### Fortalezas:
- Arquitectura modular y escalable
- Separación clara frontend/backend
- Procesamiento asíncrono eficiente
- Despliegue automatizado en Render

---

**Documento generado para:** Customer AI Driven Feedback Analyzer v3.1.0
**Última actualización:** 2024-09-17
**Próxima revisión:** 2024-10-17