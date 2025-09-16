# Arquitectura del Sistema

## Visión General

El **Customer AI Driven Feedback Analyzer** utiliza una arquitectura de microservicios simplificada desplegada en Render.com, optimizada para análisis masivo de feedback con IA.

## Topología de Servicios

### 1. Servicio Web (Público)
**Tecnología**: Node.js 18+ con React + TypeScript
**Función**: Backend-for-Frontend (BFF) y servidor de aplicación
**Características**:
- Sirve la aplicación React en producción
- Proxy reverso para llamadas API (`/api/*`)
- Elimina necesidad de CORS
- Puerto: 3000

### 2. Servicio API (Privado)
**Tecnología**: Python 3.11+ con FastAPI
**Función**: Orquestación y lógica de negocio
**Características**:
- No expuesto a Internet directamente
- Maneja uploads, validación y coordinación
- Gestiona tasks asíncronas con Celery
- Puerto interno: 8000

### 3. Servicio Worker (Privado)
**Tecnología**: Python 3.11+ con Celery
**Función**: Procesamiento asíncrono y llamadas a OpenAI
**Características**:
- Procesamiento paralelo de batches
- Rate limiting inteligente
- Reintentos con backoff exponencial
- Concurrencia configurable (default: 4)

### 4. Redis (Externo)
**Proveedor**: Upstash o Redis privado
**Función**: Message broker y cache de resultados
**Características**:
- Broker para Celery tasks
- Almacenamiento temporal de resultados
- TTL configurable (default: 24h)
- Gestión de estado de tasks

## Flujo de Comunicación

```mermaid
sequenceDiagram
    participant B as Browser
    participant W as Web (BFF)
    participant A as API (Private)
    participant R as Redis
    participant K as Worker
    participant O as OpenAI

    B->>W: Upload File
    W->>A: Proxy /api/upload
    A->>A: Validate & Parse
    A->>R: Enqueue Task
    R->>K: Dispatch Task
    K->>O: Batch Analysis (Responses API)
    O->>K: Structured Output
    K->>R: Store Results
    B->>W: Poll Status
    W->>A: Proxy /api/status
    A->>R: Check Progress
    R->>A: Progress Data
    A->>W: Status Response
    W->>B: Update UI
```

## Estructura del Monorepo

```
customer-feedback-app/
├─ api/                        # Backend FastAPI + Celery
│  ├─ app/
│  │  ├─ main.py              # Entry point (≤150 loc)
│  │  ├─ routes/              # Endpoints REST
│  │  ├─ services/            # Orquestación
│  │  ├─ core/                # Reglas de negocio
│  │  ├─ adapters/            # Integraciones externas
│  │  ├─ workers/             # Tasks Celery
│  │  ├─ schemas/             # Modelos Pydantic
│  │  └─ utils/               # Utilidades
│  └─ requirements.txt
│
├─ web/                        # Frontend React + BFF
│  ├─ src/
│  │  ├─ app/                 # Routing y páginas
│  │  ├─ components/          # UI reutilizable
│  │  ├─ features/            # Módulos funcionales
│  │  ├─ api/                 # Cliente tipado
│  │  └─ styles/              # Tailwind config
│  ├─ server/
│  │  └─ server.ts           # BFF proxy (≤150 loc)
│  └─ package.json
│
├─ docs/                       # Documentación pública
├─ tools/                      # Scripts y utilidades
└─ local-reports/             # Docs internas (EN)
```

## Principios Arquitectónicos

### 1. Anti-Overengineering
- Sin abstracciones prematuras
- Código directo y legible
- Optimización solo cuando sea medible

### 2. Modularidad Estricta
- Archivos ≤250 líneas
- Entry points ≤150 líneas
- Separación clara de responsabilidades
- Sin circular dependencies

### 3. Sin Estado de Usuario
- No hay sistema de autenticación
- Tasks identificadas por UUID
- Resultados con TTL automático

### 4. Proxy Pattern (BFF)
- Frontend solo habla con su servidor
- Elimina complejidad de CORS
- Centraliza configuración de API

## Capas de la Arquitectura

### Capa de Presentación (Web)
```typescript
// components/: UI puro, sin lógica de negocio
// features/: Módulos con estado y lógica
// api/: Cliente HTTP tipado con TypeScript
```

### Capa de Aplicación (API)
```python
# routes/: Endpoints REST, validación entrada
# services/: Casos de uso, orquestación
# schemas/: Contratos I/O con Pydantic
```

### Capa de Dominio (Core)
```python
# core/: Reglas de negocio puras
# - emotions.py: Lógica de análisis emocional
# - nps.py: Cálculos NPS
# - churn.py: Modelo de predicción
# - pain_points.py: Extracción de temas
```

### Capa de Infraestructura
```python
# adapters/: Integraciones externas
# - openai_client.py: Cliente Responses API
# - storage.py: Manejo de archivos
# - redis_client.py: Gestión de cache
```

## Escalabilidad

### Horizontal
- Workers Celery escalables independientemente
- Redis cluster para alto volumen
- CDN para assets estáticos

### Vertical
- Batch size dinámico (30-100 comentarios)
- Concurrencia ajustable por worker
- Rate limiting adaptativo

### Límites Actuales
- Max file size: 20MB
- Max comentarios: ~5000 por archivo
- Max concurrent tasks: 10 por instancia
- Rate limit: 80% del tier OpenAI

## Seguridad

### Validación de Entrada
- Whitelist de extensiones (.xlsx, .xls, .csv)
- Límite de tamaño estricto
- Sanitización de nombres de archivo
- Validación de columnas obligatorias

### Aislamiento de Red
- API y Workers no expuestos públicamente
- Comunicación interna via red privada Render
- Secrets en variables de entorno

### Gestión de Datos
- TTL automático (24h default)
- Sin persistencia de datos sensibles
- Logs sin información PII
- Resultados anónimos agregados

## Observabilidad

### Health Checks
```python
GET /api/health
{
  "status": "healthy",
  "services": {
    "api": "up",
    "redis": "connected",
    "celery": "4 workers active"
  },
  "timestamp": "2025-09-16T10:00:00Z"
}
```

### Logging Estructurado
```json
{
  "level": "INFO",
  "timestamp": "2025-09-16T10:00:00Z",
  "trace_id": "abc-123",
  "service": "api",
  "message": "Task completed",
  "duration_ms": 8500,
  "rows_processed": 850
}
```

### Métricas Clave
- **Latencia P50/P95/P99**
- **Throughput** (requests/min)
- **Error rate** por endpoint
- **Queue depth** (tasks pendientes)
- **Worker utilization**
- **OpenAI API usage**

## Decisiones Técnicas Clave

### ¿Por qué BFF?
- Elimina CORS complexity
- Centraliza configuración
- Mejora seguridad (API privada)
- Simplifica frontend

### ¿Por qué Celery?
- Robusto y battle-tested
- Excelente con Redis
- Retry mechanism built-in
- Visibilidad de tasks

### ¿Por qué Responses API?
- Structured Outputs garantizados
- Mejor manejo de streaming
- Event-driven architecture
- Diseñado para reasoning models

### ¿Por qué Render?
- Simplicidad de despliegue
- Red privada incluida
- Auto-scaling disponible
- Costo predecible

## Próximos Pasos

### Corto Plazo (v3.2)
- [ ] Implementar webhooks de notificación
- [ ] Cache de resultados frecuentes
- [ ] Dashboard de métricas básicas

### Mediano Plazo (v4.0)
- [ ] Multi-tenant con API keys
- [ ] Histórico de análisis
- [ ] Comparación temporal
- [ ] Export templates personalizables

### Largo Plazo (v5.0)
- [ ] Fine-tuning de modelos propios
- [ ] Análisis predictivo
- [ ] Integración con CRMs
- [ ] API pública documentada