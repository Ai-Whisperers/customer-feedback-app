# Guía de Despliegue en Render

## Visión General

Esta guía detalla el proceso completo para desplegar el Customer Feedback Analyzer en Render.com con arquitectura de 3 servicios + Redis.

## Pre-requisitos

- Cuenta en [Render.com](https://render.com)
- Cuenta en [OpenAI](https://platform.openai.com) con API key
- Repositorio Git (GitHub, GitLab o Bitbucket)
- Redis externo (Upstash recomendado) o plan Render con Redis

## Arquitectura de Servicios

```
┌─────────────────────────────────────────────────┐
│                   Internet                      │
└─────────────────────────────────────────────────┘
                        │
                        ▼
            ┌──────────────────┐
            │   Web Service    │  (Público)
            │   Node.js + BFF  │  Port 3000
            └──────────────────┘
                        │
                   Private Network
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
┌──────────────────┐         ┌──────────────────┐
│   API Service    │         │  Worker Service  │
│     FastAPI      │         │     Celery       │
│   (Privado)      │         │   (Privado)      │
└──────────────────┘         └──────────────────┘
        │                               │
        └───────────────┬───────────────┘
                        ▼
                ┌──────────────────┐
                │      Redis       │
                │   (External)     │
                └──────────────────┘
```

## Paso 1: Configurar Redis Externo

### Opción A: Upstash (Recomendado)

1. Crear cuenta en [Upstash](https://upstash.com)
2. Crear nuevo Redis Database:
   - **Name**: feedback-analyzer-redis
   - **Region**: Seleccionar más cercana a Render (US-West-1)
   - **Type**: Regional
   - **Eviction**: allkeys-lru
   - **Max Size**: 256MB (plan gratuito)

3. Copiar Redis URL:
```
redis://default:YOUR_PASSWORD@YOUR_ENDPOINT.upstash.io:PORT
```

### Opción B: Redis en Render (Pago)

1. En Render Dashboard → New → Redis
2. Configurar:
   - **Name**: feedback-redis
   - **Plan**: Starter ($7/mes mínimo)
   - **Maxmemory Policy**: allkeys-lru

## Paso 2: Preparar Repositorio

### 2.1 Estructura de Archivos

```
customer-feedback-app/
├── api/
│   ├── app/
│   ├── requirements.txt
│   ├── render.yaml         # Config específica API
│   └── start.sh           # Script de inicio
├── web/
│   ├── src/
│   ├── server/
│   ├── package.json
│   ├── render.yaml        # Config específica Web
│   └── build.sh          # Script de build
├── render.yaml            # Config principal
└── .env.example
```

### 2.2 Archivo render.yaml Principal

```yaml
services:
  # 1. Web Service (Público)
  - type: web
    name: feedback-analyzer-web
    runtime: node
    repo: https://github.com/YOUR_USER/customer-feedback-app
    buildCommand: cd web && npm install && npm run build
    startCommand: cd web && node server/server.js
    envVars:
      - key: NODE_ENV
        value: production
      - key: API_PROXY_TARGET
        value: https://feedback-analyzer-api.onrender.com
      - key: PORT
        value: 3000
    healthCheckPath: /api/health
    plan: starter

  # 2. API Service (Privado)
  - type: privateweb
    name: feedback-analyzer-api
    runtime: python
    repo: https://github.com/YOUR_USER/customer-feedback-app
    buildCommand: |
      cd api
      pip install --upgrade pip
      pip install -r requirements.txt
    startCommand: cd api && uvicorn app.main:app --host 0.0.0.0 --port 8000
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: OPENAI_API_KEY
        fromSecret: openai-api-key
      - key: REDIS_URL
        fromSecret: redis-url
      - key: CELERY_BROKER_URL
        fromSecret: redis-url
      - key: CELERY_RESULT_BACKEND
        fromSecret: redis-url
      - key: APP_ENV
        value: production
      - key: FILE_MAX_MB
        value: 20
      - key: MAX_BATCH_SIZE
        value: 50
      - key: MAX_RPS
        value: 8
    plan: starter

  # 3. Worker Service (Background)
  - type: worker
    name: feedback-analyzer-worker
    runtime: python
    repo: https://github.com/YOUR_USER/customer-feedback-app
    buildCommand: |
      cd api
      pip install --upgrade pip
      pip install -r requirements.txt
    startCommand: |
      cd api && celery -A app.workers.celery_app worker \
        --loglevel=INFO \
        --concurrency=4 \
        --max-tasks-per-child=100
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: OPENAI_API_KEY
        fromSecret: openai-api-key
      - key: REDIS_URL
        fromSecret: redis-url
      - key: CELERY_BROKER_URL
        fromSecret: redis-url
      - key: CELERY_RESULT_BACKEND
        fromSecret: redis-url
      - key: AI_MODEL
        value: gpt-4o-mini
      - key: RESULTS_TTL_SECONDS
        value: 86400
    plan: starter
```

### 2.3 Scripts de Inicio

**api/start.sh:**
```bash
#!/bin/bash
set -e

echo "Starting FastAPI application..."

# Verificar conexiones
python -c "
import redis
import os
r = redis.from_url(os.getenv('REDIS_URL'))
r.ping()
print('Redis connection OK')
"

# Iniciar aplicación
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port ${PORT:-8000} \
  --workers 1 \
  --loop uvloop \
  --log-level info
```

**web/build.sh:**
```bash
#!/bin/bash
set -e

echo "Building React application..."

# Install dependencies
npm ci --only=production

# Build frontend
npm run build

# Compile TypeScript server
npx tsc server/server.ts --outDir dist/server

echo "Build completed successfully"
```

## Paso 3: Configurar Variables de Entorno

### 3.1 Crear Secrets en Render

1. Dashboard → Account Settings → Environment
2. Crear Environment Group: `feedback-analyzer-secrets`
3. Agregar secrets:

```env
# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Redis (Upstash)
REDIS_URL=redis://default:password@endpoint.upstash.io:port

# Seguridad
SECRET_KEY=your-secret-key-min-32-chars
ENCRYPTION_KEY=your-encryption-key

# Opcional: Monitoring
SENTRY_DSN=https://xxx@sentry.io/xxx
```

### 3.2 Variables por Servicio

**Web Service:**
```env
NODE_ENV=production
API_PROXY_TARGET=https://feedback-analyzer-api.onrender.com
PORT=3000
BUILD_PATH=./build
```

**API Service:**
```env
APP_ENV=production
ALLOWED_ORIGINS=https://feedback-analyzer-web.onrender.com
FILE_MAX_MB=20
TMP_DIR=/tmp
MAX_CONCURRENT_TASKS=10
LOG_LEVEL=INFO
```

**Worker Service:**
```env
CELERY_TASK_ALWAYS_EAGER=False
CELERY_TASK_EAGER_PROPAGATES=False
CELERY_WORKER_PREFETCH_MULTIPLIER=1
CELERY_TASK_ACKS_LATE=True
CELERY_TASK_REJECT_ON_WORKER_LOST=True
```

## Paso 4: Desplegar

### 4.1 Método Manual

1. **Crear servicios individualmente:**
   - New → Web Service → Import Git Repository
   - Configurar cada servicio según render.yaml
   - Aplicar Environment Groups

2. **Orden de despliegue:**
   1. Redis (si usa Render Redis)
   2. API Service
   3. Worker Service
   4. Web Service

### 4.2 Método Automático (Blueprint)

1. **Crear Blueprint:**
   - New → Blueprint
   - Connect Repository
   - Render detectará `render.yaml`

2. **Configurar y Deploy:**
   - Revisar configuración
   - Apply environment groups
   - Click "Apply"

## Paso 5: Configuración Post-Deploy

### 5.1 Verificar Health Checks

```bash
# Web service
curl https://feedback-analyzer-web.onrender.com/api/health

# API service (desde Web service shell)
curl http://feedback-analyzer-api:8000/health
```

### 5.2 Configurar Custom Domain (Opcional)

1. Web Service → Settings → Custom Domains
2. Add Custom Domain: `feedback.tudominio.com`
3. Configurar DNS:
```
CNAME feedback.tudominio.com → feedback-analyzer-web.onrender.com
```

### 5.3 Configurar Auto-Deploy

1. Service → Settings → Build & Deploy
2. Enable Auto-Deploy from branch `main`
3. Configure deploy hooks si es necesario

## Paso 6: Monitoreo

### 6.1 Logs

```bash
# Ver logs en tiempo real
render logs feedback-analyzer-web --tail

# Ver logs de worker
render logs feedback-analyzer-worker --tail
```

### 6.2 Métricas Render

Dashboard → Service → Metrics:
- CPU Usage
- Memory Usage
- Response Time
- Request Count
- Error Rate

### 6.3 Alertas

1. Service → Settings → Health & Alerts
2. Configurar:
   - Health check failures
   - High CPU/Memory
   - Response time thresholds

## Troubleshooting

### Problema: "502 Bad Gateway"

**Causa**: API service no responde
**Solución**:
```bash
# Verificar logs del API
render logs feedback-analyzer-api --tail

# Reiniciar servicio
render restart feedback-analyzer-api
```

### Problema: "Task timeout"

**Causa**: Worker no procesa tasks
**Solución**:
```bash
# Verificar worker status
render ssh feedback-analyzer-worker
celery -A app.workers.celery_app inspect active

# Limpiar queue si es necesario
celery -A app.workers.celery_app purge
```

### Problema: "Redis connection refused"

**Causa**: URL incorrecta o Redis down
**Solución**:
```python
# Test connection
import redis
import os

r = redis.from_url(os.getenv('REDIS_URL'))
print(r.ping())  # Should return True
```

### Problema: "Out of memory"

**Causa**: Plan insufficient o memory leak
**Solución**:
1. Upgrade plan (Starter → Standard)
2. Ajustar concurrencia:
```env
CELERY_WORKER_CONCURRENCY=2  # Reducir de 4 a 2
MAX_BATCH_SIZE=30  # Reducir de 50 a 30
```

## Optimización de Costos

### Plan Recomendado Inicial

| Service | Plan | Costo/mes | Specs |
|---------|------|-----------|-------|
| Web | Starter | $7 | 512MB RAM, 0.5 CPU |
| API | Starter | $7 | 512MB RAM, 0.5 CPU |
| Worker | Starter | $7 | 512MB RAM, 0.5 CPU |
| Redis | Upstash Free | $0 | 256MB, 10K commands/day |
| **Total** | | **$21/mes** | |

### Plan Escalado

| Service | Plan | Costo/mes | Specs |
|---------|------|-----------|-------|
| Web | Standard | $25 | 2GB RAM, 1 CPU |
| API | Standard | $25 | 2GB RAM, 1 CPU |
| Worker | Standard x2 | $50 | 2 instances |
| Redis | Upstash Pay-as-you-go | ~$10 | 1GB, unlimited |
| **Total** | | **~$110/mes** | |

### Tips de Optimización

1. **Auto-scaling:**
```yaml
# render.yaml
scaling:
  minInstances: 1
  maxInstances: 3
  targetCPUPercent: 70
```

2. **Caching agresivo:**
```python
# Cache results for common queries
CACHE_TTL = 3600  # 1 hour
```

3. **Batch optimization:**
```python
# Ajustar según carga
if current_load > 80:
    MAX_BATCH_SIZE = 30
else:
    MAX_BATCH_SIZE = 50
```

## Scripts de Mantenimiento

### backup-redis.sh
```bash
#!/bin/bash
# Backup Redis data

REDIS_URL=$1
BACKUP_FILE="redis-backup-$(date +%Y%m%d-%H%M%S).rdb"

redis-cli --rdb $BACKUP_FILE \
  -h $(echo $REDIS_URL | cut -d@ -f2 | cut -d: -f1) \
  -p $(echo $REDIS_URL | cut -d: -f3 | cut -d/ -f1) \
  -a $(echo $REDIS_URL | cut -d: -f2 | cut -d@ -f1)

aws s3 cp $BACKUP_FILE s3://backups/redis/
```

### health-check.sh
```bash
#!/bin/bash
# Complete health check

services=("web" "api" "worker")

for service in "${services[@]}"; do
  echo "Checking $service..."

  status=$(render status feedback-analyzer-$service)

  if [[ $status != "deployed" ]]; then
    echo "WARNING: $service is $status"
    # Send alert
  fi
done
```

## Checklist de Deploy

- [ ] Redis configurado y accesible
- [ ] Variables de entorno configuradas
- [ ] Secrets creados en Render
- [ ] Repository conectado
- [ ] Services creados en orden correcto
- [ ] Health checks pasando
- [ ] Logs sin errores críticos
- [ ] Test E2E con archivo de prueba
- [ ] Monitoreo configurado
- [ ] Backup strategy definida
- [ ] Documentation actualizada

## Recursos Adicionales

- [Render Documentation](https://render.com/docs)
- [Render CLI](https://render.com/docs/cli)
- [Status Page](https://status.render.com/)
- [Community Forum](https://community.render.com/)