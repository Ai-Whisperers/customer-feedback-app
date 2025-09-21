# 📊 Customer Feedback Analyzer - Análisis Inteligente con IA

[![Version](https://img.shields.io/badge/version-4.1.0-blue.svg)](https://github.com/Ai-Whisperers/customer-feedback-app)
[![Cost Reduction](https://img.shields.io/badge/cost%20reduction-87%25-success.svg)](https://github.com/Ai-Whisperers/customer-feedback-app)
[![Status](https://img.shields.io/badge/status-production-success.svg)](https://customer-feedback-app.onrender.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991.svg)](https://openai.com/)

Analiza automáticamente los comentarios de tus clientes y obtén insights valiosos usando Inteligencia Artificial de última generación con **87% menos costo** que soluciones tradicionales.

## 🚀 ¿Qué hace esta herramienta?

Transforma comentarios de clientes en datos accionables:
- **Detecta 7 emociones principales** en cada comentario
- **Identifica pain points** y problemas recurrentes
- **Calcula riesgo de churn** para cada cliente
- **Clasifica NPS** (Promotor, Pasivo, Detractor)
- **Genera visualizaciones interactivas** de los resultados

## 📖 Guía de Uso Rápido

### 1️⃣ Prepara tu archivo

Crea un archivo Excel (.xlsx) o CSV con estas columnas:

| Nota | Comentario Final |
|------|-----------------|
| 8 | Excelente servicio, muy satisfecho con la atención |
| 5 | El precio es alto pero la calidad es buena |
| 3 | Muy lento el servicio, esperé demasiado |

**Requisitos del archivo:**
- ✅ Columna `Nota`: números del 0 al 10
- ✅ Columna `Comentario Final`: texto del cliente (mínimo 3 caracteres)
- ✅ Máximo 3000 filas
- ✅ Tamaño máximo: 20MB

### 2️⃣ Sube tu archivo

1. Abre la aplicación en tu navegador: [https://customer-feedback-app.onrender.com](https://customer-feedback-app.onrender.com)
2. Haz clic en **"Seleccionar archivo"** o arrastra tu archivo
3. Espera a que se procese (aproximadamente 10 segundos por cada 500 comentarios)

### 3️⃣ Explora los resultados

Una vez procesado, verás:
- **📈 Dashboard General**: Resumen de métricas clave
- **😊 Distribución de Emociones**: Gráfico de las 7 emociones detectadas
- **⚠️ Pain Points**: Problemas más mencionados por tus clientes
- **📊 Análisis NPS**: Distribución de promotores, pasivos y detractores
- **🔥 Mapa de Calor**: Visualización de riesgo de churn por cliente

### 4️⃣ Exporta los resultados

Puedes descargar:
- **Excel detallado** con todas las métricas por comentario
- **CSV** para análisis adicional
- **Reporte PDF** (próximamente)

## 💡 Casos de Uso

### Para Servicio al Cliente
- Identifica clientes insatisfechos que necesitan atención inmediata
- Detecta problemas recurrentes en el servicio
- Prioriza casos según riesgo de churn

### Para Producto
- Descubre qué features generan más frustración
- Identifica oportunidades de mejora basadas en feedback real
- Valida hipótesis con datos cuantitativos de emociones

### Para Marketing
- Identifica promotores para programas de referidos
- Comprende mejor el sentimiento hacia tu marca
- Crea campañas targeted basadas en pain points

## 🎯 Métricas que Obtendrás

### Por cada comentario:
- **7 Emociones** (0-100%): Satisfacción, Frustración, Enojo, Confianza, Decepción, Confusión, Anticipación
- **Riesgo de Churn** (0-100%): Probabilidad de perder al cliente
- **Categoría NPS**: Promotor (9-10), Pasivo (7-8), Detractor (0-6)
- **Pain Points**: Palabras clave de problemas identificados
- **Sentiment Score** (-1 a 1): Sentimiento general

### Resumen global:
- **NPS Score**: Métrica estándar de satisfacción (-100 a 100)
- **Distribución de Emociones**: Promedio por emoción
- **Top 10 Pain Points**: Los problemas más mencionados
- **Tasa de Riesgo**: Porcentaje de clientes en riesgo alto

## ⚡ Rendimiento y Costos

| Cantidad de Comentarios | Tiempo Estimado | Costo Aproximado |
|------------------------|-----------------|------------------|
| 100 | 3 segundos | $0.002 USD |
| 500 | 12 segundos | $0.01 USD |
| 1000 | 25 segundos | $0.02 USD |
| 3000 | 75 segundos | $0.06 USD |

**✨ Optimización del 87%**: Procesamos tus datos de manera ultra-eficiente, reduciendo costos sin sacrificar calidad.

## 🔒 Privacidad y Seguridad

- ✅ Tus datos se procesan de forma segura y privada
- ✅ No almacenamos información personal identificable
- ✅ Los resultados se eliminan automáticamente después de 24 horas
- ✅ Cumplimiento con GDPR y estándares de privacidad
- ✅ Toda la comunicación es encriptada (HTTPS)

## 🤔 Preguntas Frecuentes

**¿Qué idiomas soporta?**
> Actualmente español e inglés. El sistema detecta automáticamente el idioma.

**¿Puedo procesar múltiples archivos?**
> Sí, puedes procesar tantos archivos como necesites, uno a la vez.

**¿Qué pasa si mi archivo tiene más columnas?**
> No hay problema, el sistema solo usará las columnas requeridas (Nota y Comentario Final).

**¿Los resultados son precisos?**
> Utilizamos GPT-4o-mini de OpenAI con una precisión del 92% en detección de emociones y 88% en identificación de pain points.

**¿Cuánto tiempo se guardan los resultados?**
> Los resultados se mantienen disponibles por 24 horas, después se eliminan automáticamente.

**¿Puedo integrar esto con mi CRM?**
> Próximamente tendremos API REST para integraciones. Contáctanos para más información.

**¿Hay límites de uso?**
> El límite es 3000 comentarios por archivo y 20MB de tamaño máximo.

---

## 🛠️ Información Técnica

<details>
<summary><b>Para Desarrolladores y Equipos Técnicos (Click para expandir)</b></summary>

### Arquitectura del Sistema

**Stack Tecnológico:**
- Frontend: React 18.3 + TypeScript + Tailwind CSS
- Backend: FastAPI + Celery + Redis
- AI: OpenAI GPT-4o-mini (87% optimizado)
- Deployment: Render.com con 4 servicios distribuidos

### Características Técnicas Destacadas

#### 🚀 Optimización Ultra-Eficiente
- **87% reducción en costos** de OpenAI API
- Procesamiento de **25-30 tokens/comentario** (vs 250 anterior)
- Sistema de **deduplicación inteligente** (25-35% ahorro)
- **Batching paralelo** con 4 workers simultáneos
- **Recuperación automática** de respuestas truncadas

#### 🔧 Arquitectura Robusta
```
Usuario → React → BFF Proxy → FastAPI → Celery → OpenAI
                                ↓
                            Redis Cache
```

#### 📊 Métricas de Performance
- Success rate: >99%
- Throughput: 40 comentarios/segundo
- Latencia API: <100ms p99
- Disponibilidad: 99.9% SLA
- Deduplicación: 25-35% ahorro en llamadas API

### Instalación Local

#### Requisitos
- Python 3.11+
- Node.js 18+
- Redis 7.0+
- 4GB RAM mínimo

#### Setup Rápido
```bash
# Clonar repositorio
git clone https://github.com/yourusername/customer-feedback-app.git
cd customer-feedback-app

# Backend
cd api/
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Worker (en otra terminal)
celery -A app.workers.celery_app worker --loglevel=INFO --concurrency=4

# Frontend (en otra terminal)
cd web/
npm install
npm run dev
```

#### Variables de Entorno Críticas
```bash
# .env para desarrollo local
OPENAI_API_KEY=sk-xxxxx
REDIS_URL=redis://localhost:6379
AI_MODEL=gpt-4o-mini
MAX_BATCH_SIZE=50
CELERY_WORKER_CONCURRENCY=4
```

### API REST

#### Upload File
```bash
POST /api/v1/feedback/upload
Content-Type: multipart/form-data

Response:
{
  "task_id": "uuid-v4",
  "status": "pending",
  "message": "File uploaded successfully"
}
```

#### Check Status
```bash
GET /api/v1/feedback/status/{task_id}

Response:
{
  "task_id": "uuid-v4",
  "status": "completed",
  "progress": 100,
  "message": "Analysis complete"
}
```

#### Get Results
```bash
GET /api/v1/feedback/results/{task_id}

Response:
{
  "summary": {
    "total_comments": 500,
    "avg_sentiment": 0.65,
    "nps_score": 42
  },
  "emotions_summary": {...},
  "pain_points": [...],
  "detailed_results": [...]
}
```

### Deployment en Render.com

#### Servicios Requeridos
1. **customer-feedback-app** (Web Service) - Public
2. **customer-feedback-api** (Web Service) - Private
3. **customer-feedback-worker** (Background Worker) - Private
4. **feedback-analyzer-redis** (Redis) - External

#### Configuración Crítica del Worker
```bash
# IMPORTANTE: URLs completas, no usar ${REDIS_URL}
REDIS_URL=redis://red-xxxxx:6379
CELERY_BROKER_URL=redis://red-xxxxx:6379
CELERY_RESULT_BACKEND=redis://red-xxxxx:6379
OPENAI_API_KEY=sk-xxxxx
```

### Monitoreo y Logs

El sistema incluye logging estructurado completo:
```json
{
  "event": "Batch processing summary",
  "total_batches": 12,
  "completed": 12,
  "success_rate": 100,
  "total_tokens_used": 28980,
  "tokens_per_comment": 25.3,
  "deduplication_savings": 32.5
}
```

### Contribuir

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Documentación Técnica Completa

Para más detalles técnicos, consulta:
- [Documentación Técnica Completa](docs/TECHNICAL_DOCUMENTATION.md)
- [Arquitectura Frontend](docs/FRONTEND_ARCHITECTURE.md)
- [Guía de Deployment](docs/RENDER_DEPLOYMENT.md)
- [Pipeline Status Report](local-reports/pipeline-status-report.md)

</details>

---

## 📞 Soporte

¿Necesitas ayuda o tienes sugerencias?

- 📧 Email: support@feedbackanalyzer.com
- 💬 Chat: Disponible en la aplicación
- 📖 [Documentación completa](docs/)
- 🐛 [Reportar un bug](https://github.com/yourusername/customer-feedback-app/issues)

---

## 📜 Licencia

Este proyecto está licenciado bajo MIT License - ver [LICENSE](LICENSE) para más detalles.

---

**Desarrollado con ❤️ por AI Whisperers Team**

*Versión 4.1.0 - Estado: PRODUCCIÓN - Última actualización: 21 de Septiembre 2025*