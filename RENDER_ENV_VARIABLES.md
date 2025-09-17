# Render Environment Variables Configuration

## ⚠️ IMPORTANTE: Configuración Manual Requerida en Render Dashboard

Los servicios están desplegados pero necesitan estas variables de entorno configuradas manualmente en el dashboard de Render.

---

## 1. customer-feedback-app (Web Service - PUBLIC)

En Render Dashboard > customer-feedback-app > Environment:

```bash
NODE_VERSION=20.11.0
NODE_ENV=production
PORT=3000
API_PROXY_TARGET=http://customer-feedback-api:10000
```

**CRÍTICO:** `API_PROXY_TARGET` debe ser exactamente `http://customer-feedback-api:10000`

---

## 2. customer-feedback-api (Private Service)

En Render Dashboard > customer-feedback-api > Environment:

```bash
PYTHON_VERSION=3.12.6
PORT=10000
APP_ENV=production
SECRET_KEY=[Generar una key de 32+ caracteres]
OPENAI_API_KEY=sk-[tu-api-key-aquí]
AI_MODEL=gpt-4o-mini
REDIS_URL=[Usar "Add from service" y seleccionar Redis]
CELERY_BROKER_URL=[Mismo que REDIS_URL]
CELERY_RESULT_BACKEND=[Mismo que REDIS_URL]
FILE_MAX_MB=20
MAX_BATCH_SIZE=50
MAX_RPS=8
RESULTS_TTL_SECONDS=86400
LOG_LEVEL=INFO
```

---

## 3. celery-worker (Background Worker)

En Render Dashboard > celery-worker > Environment:

```bash
PYTHON_VERSION=3.12.6
APP_ENV=production
SECRET_KEY=[Misma que API service]
OPENAI_API_KEY=[Misma que API service]
AI_MODEL=gpt-4o-mini
REDIS_URL=[Usar "Add from service" y seleccionar Redis]
CELERY_BROKER_URL=[Mismo que REDIS_URL]
CELERY_RESULT_BACKEND=[Mismo que REDIS_URL]
FILE_MAX_MB=20
MAX_BATCH_SIZE=50
MAX_RPS=8
RESULTS_TTL_SECONDS=86400
CELERY_WORKER_CONCURRENCY=2
LOG_LEVEL=INFO
```

---

## 4. feedback-analyzer-redis (Redis)

Este servicio se configura automáticamente. Solo verifica que esté en estado "Available".

---

## 📝 Pasos para Configurar:

### Paso 1: Generar SECRET_KEY
```python
import secrets
print(secrets.token_urlsafe(32))
```
O usa: `NtJIvemZxXOP5EBMMMagLf4VZglFrXlSoF5Bvz1Ub80`

### Paso 2: Configurar Redis URLs
1. Ve a customer-feedback-api > Environment
2. Para REDIS_URL, CELERY_BROKER_URL y CELERY_RESULT_BACKEND:
   - Click "Add Environment Variable"
   - Selecciona "Add from Service"
   - Elige "feedback-analyzer-redis"
   - Selecciona "REDIS_URL"

### Paso 3: Configurar API_PROXY_TARGET
1. Ve a customer-feedback-app > Environment
2. Añade o edita `API_PROXY_TARGET`
3. **VALOR EXACTO:** `http://customer-feedback-api:10000`

### Paso 4: Añadir OPENAI_API_KEY
1. En customer-feedback-api y celery-worker
2. Añade tu key de OpenAI (empieza con `sk-`)
3. Marca como "Sensitive" para ocultarla

---

## ✅ Verificación:

Después de configurar, verifica en:

1. **Web Health:** https://customer-feedback-app.onrender.com/health
2. **API Health (via proxy):** https://customer-feedback-app.onrender.com/api/health

Si ambos responden con `{"status": "healthy"}`, la configuración es correcta.

---

## 🔴 Troubleshooting:

### Error 502 Bad Gateway:
- Verifica que API_PROXY_TARGET = `http://customer-feedback-api:10000`
- NO uses https, NO uses .onrender.com

### Error "Cannot connect to Redis":
- Verifica que Redis esté "Available"
- Usa "Add from service" para REDIS_URL

### Error "OpenAI API key invalid":
- Verifica que la key empiece con `sk-`
- Añádela tanto en API como en Worker

---

## 🚀 Deploy Manual:

Si necesitas re-deploy manual después de configurar:

1. customer-feedback-api > Manual Deploy > Deploy latest commit
2. celery-worker > Manual Deploy > Deploy latest commit
3. customer-feedback-app > Manual Deploy > Deploy latest commit

Espera ~5 minutos para que todos los servicios estén activos.