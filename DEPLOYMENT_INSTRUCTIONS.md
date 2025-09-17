# Instrucciones de Despliegue en Render - Customer Feedback Analyzer

## URLs de Producción
- **Web Service (Público)**: https://customer-feedback-app.onrender.com/
- **API Service (Privado)**: customer-feedback-api (solo interno)
- **Redis Service**: redis://red-d3597km3jp1c73es8tcg:6379

## Variables de Entorno Críticas para Configurar en Render Dashboard

### 1. Servicio: `customer-feedback-api` (FastAPI Backend)

En el Dashboard de Render, ve a **customer-feedback-api** → **Environment** → **Environment Variables** y agrega:

```bash
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY_HERE>
```

**NOTA IMPORTANTE**: Usar la API key real que está guardada de forma segura en el archivo local-reports/secrets/secrets.md

**IMPORTANTE**: Las demás variables ya están configuradas en render.yaml

### 2. Servicio: `celery-worker` (Celery Worker)

En el Dashboard de Render, ve a **celery-worker** → **Environment** → **Environment Variables** y agrega:

```bash
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY_HERE>
```

**NOTA IMPORTANTE**: Usar la API key real que está guardada de forma segura en el archivo local-reports/secrets/secrets.md

### 3. Servicio: `customer-feedback-app` (Web/BFF)

**NO requiere configuración manual** - Todas las variables están en render.yaml

### 4. Servicio: `feedback-analyzer-redis` (Redis)

**NO requiere configuración manual** - Auto-configurado

## Variables Auto-Configuradas por render.yaml

### customer-feedback-api
- `PORT`: 10000
- `APP_ENV`: production
- `SECRET_KEY`: Auto-generada
- `AI_MODEL`: gpt-4o-mini
- `REDIS_URL`: Desde feedback-analyzer-redis
- `FILE_MAX_MB`: 20
- `MAX_BATCH_SIZE`: 50
- `MAX_RPS`: 8
- `RESULTS_TTL_SECONDS`: 86400

### celery-worker
- `APP_ENV`: production
- `SECRET_KEY`: Compartida desde customer-feedback-api
- `AI_MODEL`: gpt-4o-mini
- `REDIS_URL`: Desde feedback-analyzer-redis
- `CELERY_WORKER_CONCURRENCY`: 2
- `CELERY_MAX_TASKS_PER_CHILD`: 100

### customer-feedback-app
- `NODE_ENV`: production
- `NODE_VERSION`: 20.11.0
- `PORT`: 3000
- `API_PROXY_TARGET`: Auto-configurado desde customer-feedback-api

## Orden de Despliegue

1. **Redis primero** (feedback-analyzer-redis)
2. **API segundo** (customer-feedback-api)
3. **Worker tercero** (celery-worker)
4. **Web último** (customer-feedback-app)

## Verificación Post-Despliegue

### 1. Verificar Health Endpoints
```bash
# Web Service Health
curl https://customer-feedback-app.onrender.com/health

# API Health (a través del proxy)
curl https://customer-feedback-app.onrender.com/api/health
```

### 2. Verificar Logs
- Revisar logs de cada servicio en Render Dashboard
- Buscar errores de conexión a Redis
- Verificar que el worker está procesando tareas

### 3. Test de Funcionalidad
1. Acceder a https://customer-feedback-app.onrender.com/
2. Navegar a la página del analizador
3. Subir un archivo CSV de prueba
4. Verificar que el análisis se complete

## Solución de Problemas Comunes

### Error: "Cannot connect to Redis"
- Verificar que Redis está en estado "Running"
- Confirmar que REDIS_URL está correcta en todos los servicios

### Error: "OpenAI API key not found"
- Agregar manualmente OPENAI_API_KEY en API y Worker services
- Reiniciar los servicios después de agregar la key

### Error: "502 Bad Gateway"
- Verificar que el servicio API está corriendo
- Revisar que API_PROXY_TARGET está configurado correctamente
- Confirmar que el puerto del API es 10000

### Error: "Failed to process file"
- Verificar que el worker está corriendo
- Revisar logs del worker para errores de OpenAI
- Confirmar que MAX_BATCH_SIZE y MAX_RPS están configurados

## Comandos Útiles

### Para desarrollo local
```bash
# Iniciar todos los servicios localmente
cd api && uvicorn app.main:app --reload &
cd api && celery -A app.workers.celery_app worker --loglevel=INFO &
cd web && npm run dev &
cd web/client && npm run dev
```

### Para verificar configuración
```bash
# Ver variables de entorno actuales
cat .env.production

# Verificar render.yaml
cat render.yaml
```

## Notas Importantes

1. **NUNCA commitear** archivos .env con keys reales
2. **Siempre usar** render.yaml para configuración base
3. **Solo agregar** manualmente las keys secretas (OPENAI_API_KEY)
4. **Verificar** que todos los servicios están en la misma región (oregon)
5. **Monitorear** el uso de Redis para evitar límites del plan gratuito

## Contacto y Soporte

Para problemas de despliegue, revisar:
1. Logs en Render Dashboard
2. Estado de servicios en https://status.render.com/
3. Documentación en https://docs.render.com/

---
**Última actualización**: 2025-09-17
**Versión**: 3.1.0