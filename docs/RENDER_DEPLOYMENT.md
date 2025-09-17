# Render Deployment Guide - Customer Feedback Analyzer

## 🚀 Quick Start

Esta guía explica cómo configurar los servicios ya desplegados en Render para que se comuniquen correctamente.

## Arquitectura en Render

```
┌────────────────┐
│  Web Service   │ ◄── Public (customer-feedback-app)
│   Port 3000    │
└────────┬───────┘
         │ Internal HTTP
         ▼
┌────────────────┐
│  API Service   │ ◄── Private (customer-feedback-api)
│  Port 10000    │
└────────┬───────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Worker │ │ Redis  │
└────────┘ └────────┘
```

## Servicios Desplegados

### 1. customer-feedback-app (Web - PUBLIC)
- **Tipo:** Web Service
- **URL:** https://customer-feedback-app.onrender.com
- **Puerto:** 3000
- **Build:** `cd web && npm install && npm run build:render`
- **Start:** `cd web && npm run start:prod`

### 2. customer-feedback-api (API - PRIVATE)
- **Tipo:** Private Service
- **URL Interna:** http://customer-feedback-api-bmjp:10000
- **Puerto:** 10000
- **Build:** `pip install -r api/requirements.txt`
- **Start:** `cd api && uvicorn app.main:app --host 0.0.0.0 --port 10000`

### 3. celery-worker (Worker - PRIVATE)
- **Tipo:** Background Worker
- **Build:** `pip install -r api/requirements.txt`
- **Start:** `cd api && celery -A app.workers.celery_app worker --loglevel=INFO`

### 4. feedback-analyzer-redis (Redis)
- **Tipo:** Redis (Managed)
- **Plan:** Free/Starter

## ⚙️ Configuración de Variables de Entorno

### Web Service (customer-feedback-app)

```bash
NODE_VERSION=20.11.0
NODE_ENV=production
PORT=3000
API_PROXY_TARGET=http://customer-feedback-api-bmjp:10000
```

**IMPORTANTE:** El `API_PROXY_TARGET` debe usar el nombre del servicio interno de Render, NO la URL pública.

### API Service (customer-feedback-api)

```bash
PYTHON_VERSION=3.12.6
PORT=10000
APP_ENV=production
SECRET_KEY=[Auto-generated or manual 32+ chars]
OPENAI_API_KEY=sk-xxx  # Tu API key de OpenAI
AI_MODEL=gpt-4o-mini
REDIS_URL=[From Redis service]
CELERY_BROKER_URL=[Same as REDIS_URL]
CELERY_RESULT_BACKEND=[Same as REDIS_URL]
FILE_MAX_MB=20
MAX_BATCH_SIZE=50
MAX_RPS=8
RESULTS_TTL_SECONDS=86400
LOG_LEVEL=INFO
```

### Worker Service (celery-worker)

```bash
# Mismas variables que API Service
PYTHON_VERSION=3.12.6
APP_ENV=production
SECRET_KEY=[Same as API]
OPENAI_API_KEY=[Same as API]
AI_MODEL=gpt-4o-mini
REDIS_URL=[From Redis service]
CELERY_BROKER_URL=[Same as REDIS_URL]
CELERY_RESULT_BACKEND=[Same as REDIS_URL]
CELERY_WORKER_CONCURRENCY=2
LOG_LEVEL=INFO
```

## 🔧 Pasos para Configurar la Comunicación

### Paso 1: Verificar Nombres de Servicios

En el dashboard de Render, verifica que los nombres de tus servicios sean exactamente:
- `customer-feedback-app` (Web)
- `customer-feedback-api` (API)
- `celery-worker` (Worker)
- `feedback-analyzer-redis` (Redis)

### Paso 2: Configurar API_PROXY_TARGET

En el servicio **customer-feedback-app**:

1. Ve a Environment → Environment Variables
2. Busca o crea `API_PROXY_TARGET`
3. Establece el valor: `http://customer-feedback-api-bmjp:10000`

   **NO uses:**
   - ❌ `https://customer-feedback-api.onrender.com`
   - ❌ `http://localhost:10000`
   - ❌ URLs externas

   **SÍ usa:**
   - ✅ `http://customer-feedback-api-bmjp:10000`

### Paso 3: Configurar Redis URL

En los servicios **customer-feedback-api** y **celery-worker**:

1. Ve a Environment → Environment Variables
2. Para `REDIS_URL`, `CELERY_BROKER_URL`, y `CELERY_RESULT_BACKEND`:
   - Si usas Redis de Render: Usa el botón "Add from service"
   - Si usas Redis externo (Upstash, RedisLabs): Pega la URL directamente

### Paso 4: Configurar OpenAI API Key

En ambos servicios **customer-feedback-api** y **celery-worker**:

1. Añade `OPENAI_API_KEY` con tu key de OpenAI
2. Marca como "Sensitive" para ocultarla

### Paso 5: Verificar Puertos

- **Web:** Puerto 3000 (público)
- **API:** Puerto 10000 (privado, interno)

Asegúrate de que el comando de inicio de API use:
```bash
--port 10000  # NO --port $PORT
```

## 🧪 Verificación de la Configuración

### 1. Test de Health Check

```bash
# Web service health
curl https://customer-feedback-app.onrender.com/health

# API health (a través del proxy)
curl https://customer-feedback-app.onrender.com/api/health
```

### 2. Verificar Logs

En el dashboard de Render, revisa los logs de cada servicio:

**Web Service debe mostrar:**
```
BFF Server Started Successfully
Port: 3000
API Target: http://customer-feedback-api-bmjp:10000
```

**API Service debe mostrar:**
```
INFO: Uvicorn running on http://0.0.0.0:10000
INFO: Application startup complete
```

**Worker debe mostrar:**
```
[INFO/MainProcess] Connected to redis://...
[INFO/MainProcess] celery@... ready
```

### 3. Test de Upload

```bash
curl -X POST https://customer-feedback-app.onrender.com/api/upload \
  -F "file=@test.csv"
```

## 🔴 Troubleshooting

### Error: "Bad Gateway" o Error 502

**Causa:** El web service no puede conectar con el API.

**Solución:**
1. Verifica que `API_PROXY_TARGET` = `http://customer-feedback-api-bmjp:10000`
2. Confirma que el API está en puerto 10000
3. Revisa que el API service esté "Running" en Render

### Error: "ECONNREFUSED" en logs

**Causa:** URL incorrecta o servicio no disponible.

**Solución:**
1. Usa el nombre interno del servicio, no localhost
2. Verifica que todos los servicios estén activos
3. Revisa los health checks

### Error: "Task processing failed"

**Causa:** Redis o Celery no configurados correctamente.

**Solución:**
1. Verifica REDIS_URL en API y Worker
2. Confirma que el Worker está corriendo
3. Revisa logs del Worker para errores

### Error: "OpenAI API key invalid"

**Causa:** OPENAI_API_KEY no configurada o inválida.

**Solución:**
1. Añade OPENAI_API_KEY en API y Worker
2. Verifica que la key empiece con `sk-`
3. Confirma que la key tiene créditos disponibles

## 📝 Checklist de Deployment

- [ ] Servicios creados con nombres correctos
- [ ] Redis configurado y conectado
- [ ] `API_PROXY_TARGET` = `http://customer-feedback-api-bmjp:10000`
- [ ] `OPENAI_API_KEY` configurada en API y Worker
- [ ] `SECRET_KEY` generada (32+ caracteres)
- [ ] `REDIS_URL` configurada en API y Worker
- [ ] Puerto 10000 en API service
- [ ] Health checks pasando
- [ ] Logs sin errores
- [ ] Test de upload funcionando

## 🔄 Auto-Deploy

El archivo `render.yaml` está configurado para auto-deploy:
- Push a `main` branch dispara deploy automático
- Cada servicio tiene `buildFilter` para deployments selectivos

## 📊 Monitoreo

1. **Health Checks:**
   - Web: `/health`
   - API: `/health` (via proxy: `/api/health`)

2. **Métricas en Render Dashboard:**
   - CPU y memoria usage
   - Request count
   - Response times
   - Error rates

3. **Logs:**
   - Filtrar por nivel (INFO, ERROR)
   - Buscar por timestamp
   - Download logs para análisis

## 🆘 Soporte

Si los servicios siguen sin comunicarse:

1. Verifica que uses la rama `main` actualizada
2. Revisa que el `render.yaml` esté sincronizado
3. Confirma las variables de entorno una por una
4. Contacta soporte de Render con los service IDs

## Referencias

- [Render Private Services](https://docs.render.com/private-services)
- [Service Discovery](https://docs.render.com/service-discovery)
- [Environment Variables](https://docs.render.com/environment-variables)