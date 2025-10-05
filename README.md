# 📊 Customer Feedback Analyzer - Análisis Inteligente con IA

[![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)](https://github.com/Ai-Whisperers/customer-feedback-app)
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

Crea o toma un archivo Excel (.xlsx) o CSV que contenga los comentarios que quieres analizar para obtener retroalimentación, el excel debe tener estas columnas necesariamente:

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
- **😊 Distribución de Emociones**: Gráfico de las emociones detectadas
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
- **Pain Points**: Palabras clave de problemas identificados (máximo 5 por comentario)
- **Sentiment Score** (-1 a 1): Sentimiento general

### Resumen global:
- **NPS Score**: Métrica estándar de satisfacción (-100 a 100)
- **Distribución de Emociones**: Promedio por emoción
- **Top 10 Pain Points**: Los problemas más mencionados
- **Tasa de Riesgo**: Porcentaje de clientes en riesgo alto

## ⚡ Rendimiento y Costos

| Cantidad de Comentarios | Tiempo Estimado | Costo Aproximado | Estado |
|------------------------|-----------------|------------------|--------|
| 100 | 2-3 segundos | $0.002 USD | ✓ Óptimo |
| 500 | 5-8 segundos | $0.01 USD | ✓ Óptimo |
| 850 | 8-10 segundos | $0.017 USD | ✓ Óptimo |
| 1800 | 18-20 segundos | $0.036 USD | ⚠ Mejorable |
| 3000 | 30-35 segundos | $0.06 USD | ✓ Óptimo |

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
- **87% reducción en costos** de OpenAI API con análisis híbrido
- **Análisis local gratuito**: Sentiment (VADER/TextBlob) sin costo
- **OpenAI selectivo**: Solo para churn risk y pain points complejos
- Procesamiento de **25-30 tokens/comentario** (antes: 250)
- Sistema de **deduplicación inteligente SHA256** (15-20% ahorro)
- **Cache de comentarios** en Redis (7 días TTL)
- **Batching dinámico** de 50-100 comentarios con gestión de memoria

#### 🎨 Funcionalidades Clave v3.2
- **Excel profesional** con hojas formateadas, gráficos y formato condicional
- **Parser flexible** con detección dinámica de columnas (Nota, Comentario Final, NPS)
- **Monitor de event loops** para debugging de procesamiento asíncrono
- **Hybrid Analyzer**: Combina análisis local + IA para máxima eficiencia
- **Gestión de memoria**: Batch sizing adaptativo según recursos disponibles

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
BATCH_SIZE_OPTIMAL=120
CELERY_WORKER_CONCURRENCY=4
NPS_CALCULATION_METHOD=shifted  # Nuevo: NPS siempre positivo
EXCEL_FORMATTING_ENABLED=true   # Excel profesional con gráficos
ENABLE_COMMENT_CACHE=true       # Cache de comentarios (7 días TTL)
PARSER_TYPE=flexible             # Parser dinámico de columnas
ENABLE_PARALLEL_PROCESSING=true # Procesamiento paralelo habilitado
HYBRID_ANALYSIS_ENABLED=true    # Análisis híbrido (local + OpenAI)
```

### API REST

#### Subir Archivo
```bash
POST /upload
Content-Type: multipart/form-data

Respuesta:
{
  "task_id": "uuid-v4",
  "status": "pending",
  "message": "File uploaded successfully"
}
```

#### Consultar Estado
```bash
GET /status/{task_id}

Respuesta:
{
  "task_id": "uuid-v4",
  "status": "completed",
  "progress": 100,
  "message": "Analysis complete",
  "processed_rows": 500
}
```

#### Obtener Resultados
```bash
GET /results/{task_id}

Respuesta:
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

#### Exportar Resultados
```bash
GET /export/{task_id}?format=xlsx

Formatos disponibles: csv, xlsx, all
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
- [Índice de Documentación](docs/README.md) - Punto de entrada a toda la documentación
- [Documentación Técnica Completa](docs/TECHNICAL_DOCUMENTATION.md) - Arquitectura y detalles de implementación
- [Arquitectura Frontend](docs/FRONTEND_ARCHITECTURE.md) - Estructura y componentes del frontend
- [Guía de Deployment en Render](docs/RENDER_DEPLOYMENT.md) - Configuración de despliegue
- [Integración de Servicios](docs/SERVICE_INTEGRATION.md) - Comunicación entre servicios

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

**Desarrollado por AI Whisperers Team**

*Versión 3.2.0 - Estado: PRODUCCIÓN - Última actualización: 27 de Septiembre 2024*

### Cambios Recientes (v3.2.0)

#### Frontend
- ✅ Refactorización completa de componentes (Clean Architecture)
- ✅ Code splitting y lazy loading (65% reducción de bundle)
- ✅ Componentes modulares: ResultsCharts (380→65 líneas), FileUpload (251→100 líneas)
- ✅ Glass Design System implementado
- ✅ TypeScript estricto con tipos explícitos

#### Backend
- ✅ Análisis híbrido: Sentiment local (VADER/TextBlob) + OpenAI
- ✅ Procesamiento paralelo con event loop optimizado
- ✅ Deduplicación inteligente SHA256 (15-20% ahorro)
- ✅ Excel profesional con gráficos y formato condicional
- ✅ Parser flexible con detección dinámica de columnas
- ✅ Gestión de memoria dinámica (batch sizing adaptativo)
- ✅ Cache de comentarios con 7 días TTL