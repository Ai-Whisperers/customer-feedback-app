# API Reference - Customer Feedback Analyzer

## Base URL

```
Desarrollo: http://localhost:3000/api
Producción: https://your-app.onrender.com/api
```

## Autenticación

Actualmente el sistema no requiere autenticación. En futuras versiones se implementará API Key authentication.

## Endpoints

### 1. Upload File

Carga un archivo de comentarios para análisis.

**Endpoint:** `POST /api/upload`

**Headers:**
```http
Content-Type: multipart/form-data
```

**Request Body:**
```typescript
{
  file: File, // .xlsx, .xls o .csv
  options?: {
    language_hint?: 'es' | 'en' | 'auto',
    segment?: string,
    priority?: 'normal' | 'high'
  }
}
```

**Response (200 OK):**
```json
{
  "task_id": "t_abc123def456",
  "status": "queued",
  "estimated_time_seconds": 15,
  "file_info": {
    "name": "comentarios_q3.xlsx",
    "rows": 850,
    "size_mb": 2.3
  }
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Archivo inválido",
  "details": "Columnas requeridas no encontradas: Nota, Comentario Final",
  "code": "INVALID_FILE_FORMAT"
}
```

**Response (413 Payload Too Large):**
```json
{
  "error": "Archivo demasiado grande",
  "details": "El archivo excede el límite de 20MB",
  "code": "FILE_TOO_LARGE"
}
```

**Validaciones:**
- Extensiones permitidas: `.xlsx`, `.xls`, `.csv`
- Tamaño máximo: 20MB
- Columnas obligatorias: `Nota` (0-10), `Comentario Final` (min 3 caracteres)
- Columna opcional: `NPS` (si no existe, se calcula automáticamente)

---

### 2. Get Task Status

Obtiene el estado actual de una tarea de análisis.

**Endpoint:** `GET /api/status/:task_id`

**Parameters:**
- `task_id` (string, required): ID de la tarea retornado por `/upload`

**Response (200 OK) - En Proceso:**
```json
{
  "task_id": "t_abc123def456",
  "status": "processing",
  "progress": 45,
  "current_step": "Analizando batch 3 de 7",
  "estimated_remaining_seconds": 8,
  "started_at": "2025-09-16T10:00:00Z",
  "messages": [
    "Archivo validado correctamente",
    "850 comentarios detectados",
    "Procesando en 7 batches"
  ]
}
```

**Response (200 OK) - Completado:**
```json
{
  "task_id": "t_abc123def456",
  "status": "completed",
  "progress": 100,
  "completed_at": "2025-09-16T10:00:15Z",
  "duration_seconds": 15,
  "results_available": true
}
```

**Response (200 OK) - Error:**
```json
{
  "task_id": "t_abc123def456",
  "status": "failed",
  "error": "Error en el análisis",
  "details": "Rate limit excedido en OpenAI API",
  "failed_at": "2025-09-16T10:00:10Z",
  "retry_available": true
}
```

**Response (404 Not Found):**
```json
{
  "error": "Tarea no encontrada",
  "details": "La tarea ha expirado o no existe",
  "code": "TASK_NOT_FOUND"
}
```

**Estados Posibles:**
- `queued`: En cola esperando procesamiento
- `processing`: Actualmente en análisis
- `completed`: Análisis completado exitosamente
- `failed`: Error durante el procesamiento
- `expired`: Resultados expirados (>24h)

---

### 3. Get Results

Obtiene los resultados detallados del análisis.

**Endpoint:** `GET /api/results/:task_id`

**Parameters:**
- `task_id` (string, required): ID de la tarea

**Query Parameters:**
- `format` (string, optional): `json` (default) | `summary`
- `include_rows` (boolean, optional): Incluir análisis por fila (default: true)

**Response (200 OK):**
```json
{
  "task_id": "t_abc123def456",
  "metadata": {
    "total_comments": 850,
    "processing_time_seconds": 15,
    "model_used": "gpt-4o-mini",
    "timestamp": "2025-09-16T10:00:15Z"
  },
  "summary": {
    "nps": {
      "score": 42,
      "promoters": 412,
      "promoters_percentage": 48.5,
      "passives": 256,
      "passives_percentage": 30.1,
      "detractors": 182,
      "detractors_percentage": 21.4
    },
    "emotions": {
      "alegria": 0.42,
      "confianza": 0.38,
      "anticipacion": 0.15,
      "sorpresa_positiva": 0.12,
      "amor": 0.08,
      "optimismo": 0.22,
      "admiracion": 0.18,
      "miedo": 0.15,
      "tristeza": 0.12,
      "enojo": 0.18,
      "disgusto": 0.08,
      "sorpresa_negativa": 0.05,
      "verguenza": 0.03,
      "culpa": 0.02,
      "interes": 0.35,
      "confusion": 0.22
    },
    "churn_risk": {
      "average": 0.23,
      "high_risk_count": 85,
      "high_risk_percentage": 10.0,
      "distribution": {
        "very_low": 340,
        "low": 255,
        "moderate": 170,
        "high": 68,
        "very_high": 17
      }
    },
    "pain_points": [
      {
        "issue": "tiempo_espera",
        "frequency": 134,
        "percentage": 15.8,
        "examples": [
          "La espera fue demasiado larga",
          "Tardaron mucho en atenderme"
        ]
      },
      {
        "issue": "precio_alto",
        "frequency": 98,
        "percentage": 11.5,
        "examples": [
          "Muy caro para lo que ofrecen",
          "El precio no justifica la calidad"
        ]
      }
    ],
    "sentiment_distribution": {
      "muy_positivo": 180,
      "positivo": 285,
      "neutral": 200,
      "negativo": 145,
      "muy_negativo": 40
    },
    "languages_detected": {
      "es": 750,
      "en": 100
    }
  },
  "rows": [
    {
      "index": 0,
      "original_text": "Excelente servicio, muy recomendado",
      "nota": 9,
      "nps_category": "promoter",
      "emotions": {
        "alegria": 0.85,
        "confianza": 0.75,
        "admiracion": 0.60
      },
      "churn_risk": 0.05,
      "pain_points": [],
      "sentiment": "muy_positivo",
      "language": "es"
    }
  ],
  "aggregated_insights": {
    "top_positive_themes": [
      "calidad_servicio",
      "atencion_personal",
      "rapidez"
    ],
    "top_negative_themes": [
      "precio",
      "tiempo_espera",
      "comunicacion"
    ],
    "recommendations": [
      "Reducir tiempos de espera en horas pico",
      "Revisar estrategia de precios",
      "Mejorar comunicación de procesos"
    ],
    "segment_analysis": {
      "promoters_profile": {
        "dominant_emotions": ["alegria", "confianza"],
        "common_mentions": ["excelente", "recomiendo", "perfecto"]
      },
      "detractors_profile": {
        "dominant_emotions": ["enojo", "frustración"],
        "common_mentions": ["mal", "pésimo", "nunca más"]
      }
    }
  }
}
```

**Response (404 Not Found):**
```json
{
  "error": "Resultados no encontrados",
  "details": "La tarea no se ha completado o ha expirado",
  "code": "RESULTS_NOT_FOUND"
}
```

---

### 4. Export Results

Descarga los resultados en formato CSV o Excel.

**Endpoint:** `GET /api/export/:task_id`

**Parameters:**
- `task_id` (string, required): ID de la tarea

**Query Parameters:**
- `format` (string, required): `csv` | `xlsx`
- `include` (string, optional): `all` | `summary` | `detailed` (default: all)

**Response (200 OK):**
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="analysis_t_abc123def456.xlsx"

[Binary Excel/CSV file]
```

**Excel Structure (xlsx):**
- **Hoja 1 - Resumen**: Métricas agregadas, NPS score, distribuciones
- **Hoja 2 - Detalle**: Análisis fila por fila con todas las métricas
- **Hoja 3 - Pain Points**: Ranking de problemas detectados
- **Hoja 4 - Emociones**: Matriz de emociones por comentario
- **Hoja 5 - Insights**: Recomendaciones y análisis segmentado

**CSV Structure:**
```csv
index,texto_original,nota,nps_category,alegria,confianza,...,churn_risk,pain_points,sentiment,language
0,"Excelente servicio",9,promoter,0.85,0.75,...,0.05,"",muy_positivo,es
1,"Muy mal servicio",2,detractor,0.05,0.10,...,0.85,"tiempo_espera;precio",muy_negativo,es
```

---

### 5. Health Check

Verifica el estado de los servicios.

**Endpoint:** `GET /api/health`

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-16T10:00:00Z",
  "services": {
    "api": {
      "status": "up",
      "response_time_ms": 5
    },
    "redis": {
      "status": "connected",
      "memory_used_mb": 45,
      "memory_available_mb": 455,
      "active_connections": 3
    },
    "celery": {
      "status": "active",
      "workers": 4,
      "active_tasks": 2,
      "queued_tasks": 5
    },
    "openai": {
      "status": "reachable",
      "rate_limit_remaining": 450,
      "rate_limit_reset": "2025-09-16T10:01:00Z"
    }
  },
  "metrics": {
    "tasks_last_hour": 125,
    "average_processing_time": 12.5,
    "success_rate": 0.98
  }
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "timestamp": "2025-09-16T10:00:00Z",
  "services": {
    "redis": {
      "status": "disconnected",
      "error": "Connection refused"
    }
  },
  "message": "Algunos servicios no están disponibles"
}
```

---

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| `INVALID_FILE_FORMAT` | Formato de archivo no soportado |
| `FILE_TOO_LARGE` | Archivo excede límite de tamaño |
| `MISSING_COLUMNS` | Columnas obligatorias no encontradas |
| `INVALID_DATA` | Datos inválidos en el archivo |
| `TASK_NOT_FOUND` | Tarea no existe o ha expirado |
| `RESULTS_NOT_FOUND` | Resultados no disponibles |
| `PROCESSING_ERROR` | Error durante el procesamiento |
| `RATE_LIMIT_EXCEEDED` | Límite de requests excedido |
| `SERVICE_UNAVAILABLE` | Servicio temporalmente no disponible |
| `INTERNAL_ERROR` | Error interno del servidor |

---

## Rate Limiting

- **Límite por IP**: 100 requests por minuto
- **Límite de uploads**: 10 archivos por hora
- **Límite de tareas concurrentes**: 5 por IP
- **Tamaño máximo total por hora**: 100MB

**Headers de Rate Limit:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1631784000
```

---

## WebSocket Events (Próximamente)

Para actualizaciones en tiempo real del progreso:

```javascript
const ws = new WebSocket('wss://your-app.onrender.com/ws');

ws.on('connect', () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    task_id: 't_abc123def456'
  }));
});

ws.on('message', (data) => {
  const event = JSON.parse(data);
  // Tipos de eventos:
  // - progress: Actualización de progreso
  // - completed: Tarea completada
  // - error: Error en procesamiento
});
```

---

## Ejemplos de Integración

### JavaScript/TypeScript

```typescript
class FeedbackAnalyzerClient {
  private baseUrl = 'https://your-app.onrender.com/api';

  async uploadFile(file: File): Promise<{ task_id: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/upload`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  async waitForResults(taskId: string, pollInterval = 1000): Promise<any> {
    while (true) {
      const status = await this.getStatus(taskId);

      if (status.status === 'completed') {
        return this.getResults(taskId);
      }

      if (status.status === 'failed') {
        throw new Error(status.error);
      }

      await new Promise(resolve => setTimeout(resolve, pollInterval));
    }
  }

  async getStatus(taskId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/status/${taskId}`);
    return response.json();
  }

  async getResults(taskId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/results/${taskId}`);
    return response.json();
  }

  async exportResults(taskId: string, format: 'csv' | 'xlsx'): Promise<Blob> {
    const response = await fetch(
      `${this.baseUrl}/export/${taskId}?format=${format}`
    );
    return response.blob();
  }
}
```

### Python

```python
import requests
import time
from typing import Dict, Any

class FeedbackAnalyzerClient:
    def __init__(self, base_url: str = "https://your-app.onrender.com/api"):
        self.base_url = base_url

    def upload_file(self, file_path: str) -> str:
        """Upload file and return task_id"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/upload",
                files=files
            )
            response.raise_for_status()
            return response.json()['task_id']

    def wait_for_results(
        self,
        task_id: str,
        poll_interval: int = 1
    ) -> Dict[str, Any]:
        """Poll until results are ready"""
        while True:
            status = self.get_status(task_id)

            if status['status'] == 'completed':
                return self.get_results(task_id)

            if status['status'] == 'failed':
                raise Exception(status['error'])

            time.sleep(poll_interval)

    def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status"""
        response = requests.get(f"{self.base_url}/status/{task_id}")
        response.raise_for_status()
        return response.json()

    def get_results(self, task_id: str) -> Dict[str, Any]:
        """Get analysis results"""
        response = requests.get(f"{self.base_url}/results/{task_id}")
        response.raise_for_status()
        return response.json()

    def export_results(
        self,
        task_id: str,
        format: str = 'xlsx',
        output_path: str = None
    ) -> None:
        """Export results to file"""
        response = requests.get(
            f"{self.base_url}/export/{task_id}",
            params={'format': format}
        )
        response.raise_for_status()

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(response.content)

# Uso
client = FeedbackAnalyzerClient()
task_id = client.upload_file("comentarios.xlsx")
results = client.wait_for_results(task_id)
print(f"NPS Score: {results['summary']['nps']['score']}")
client.export_results(task_id, 'xlsx', 'resultados.xlsx')
```

---

## Versionado

La API utiliza versionado en la URL. La versión actual es `v1`.

Futuras versiones mantendrán compatibilidad hacia atrás durante al menos 6 meses.

**Deprecation Policy:**
- Anuncio de deprecación: 3 meses antes
- Período de transición: 6 meses
- Headers de aviso: `X-API-Deprecation-Date`