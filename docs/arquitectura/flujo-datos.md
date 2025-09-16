# Flujo de Datos - Pipeline End-to-End

## Visión General del Pipeline

El sistema procesa comentarios de clientes a través de un pipeline asíncrono optimizado para alto volumen y baja latencia.

## Fases del Pipeline

### Fase 1: Ingesta de Datos

#### 1.1 Upload del Archivo
```javascript
// Frontend: Validación inicial
const validateFile = (file) => {
  const validExtensions = ['.xlsx', '.xls', '.csv'];
  const maxSizeMB = 20;

  if (!validExtensions.includes(getExtension(file.name))) {
    throw new Error('Formato no soportado');
  }

  if (file.size > maxSizeMB * 1024 * 1024) {
    throw new Error('Archivo demasiado grande');
  }
};
```

#### 1.2 Transmisión al Backend
```python
# API: Recepción y almacenamiento temporal
@router.post("/upload")
async def upload_file(file: UploadFile):
    # Validación de seguridad
    validate_file_security(file)

    # Guardar en /tmp con UUID único
    file_path = save_temp_file(file)

    # Parseo inicial para validación
    df = parse_file(file_path)
    validate_columns(df)

    # Crear task asíncrona
    task = analyze_feedback.delay(file_path)

    return {"task_id": task.id}
```

### Fase 2: Normalización y Preparación

#### 2.1 Validación de Columnas
```python
REQUIRED_COLUMNS = {
    'Nota': int,           # Obligatorio: 0-10
    'Comentario Final': str # Obligatorio: min 3 chars
}

OPTIONAL_COLUMNS = {
    'NPS': str,            # Si existe, usar directamente
    'Fecha': datetime,     # Para análisis temporal
    'Segmento': str        # Para agrupación
}
```

#### 2.2 Limpieza de Datos
```python
def normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    # Limpieza de texto
    df['Comentario Final'] = df['Comentario Final'].apply(
        lambda x: clean_text(x)
    )

    # Normalización Unicode
    df['Comentario Final'] = df['Comentario Final'].apply(
        lambda x: unicodedata.normalize('NFKD', x)
    )

    # Eliminar filas inválidas
    df = df[df['Nota'].between(0, 10)]
    df = df[df['Comentario Final'].str.len() >= 3]

    # Calcular NPS si no existe
    if 'NPS' not in df.columns:
        df['NPS'] = df['Nota'].apply(calculate_nps_category)

    return df
```

### Fase 3: Detección de Idioma

#### 3.1 Clasificación por Comentario
```python
def detect_language(text: str) -> str:
    """Detecta idioma usando heurísticas simples"""
    spanish_markers = ['ñ', 'á', 'é', 'í', 'ó', 'ú']
    spanish_words = ['el', 'la', 'de', 'que', 'en', 'por']

    text_lower = text.lower()

    # Check caracteres especiales
    if any(marker in text_lower for marker in spanish_markers):
        return 'es'

    # Check palabras comunes
    words = text_lower.split()
    spanish_count = sum(1 for word in spanish_words if word in words)

    return 'es' if spanish_count >= 2 else 'en'
```

### Fase 4: Chunking Inteligente

#### 4.1 Estrategia de Batching
```python
def create_batches(comments: List[str], max_batch_size: int = 50) -> List[List[str]]:
    """Crea batches optimizados por tokens"""
    batches = []
    current_batch = []
    current_tokens = 0

    for comment in comments:
        # Estimación simple: 1 token ≈ 4 caracteres
        estimated_tokens = len(comment) / 4

        if len(current_batch) >= max_batch_size or \
           current_tokens + estimated_tokens > MAX_TOKENS_PER_BATCH:
            batches.append(current_batch)
            current_batch = []
            current_tokens = 0

        current_batch.append(comment)
        current_tokens += estimated_tokens

    if current_batch:
        batches.append(current_batch)

    return batches
```

#### 4.2 Distribución a Workers
```python
@celery.task
def analyze_feedback(file_path: str) -> dict:
    df = load_and_normalize(file_path)
    batches = create_batches(df['Comentario Final'].tolist())

    # Crear subtasks paralelas
    job = group(
        analyze_batch.s(batch, idx)
        for idx, batch in enumerate(batches)
    )

    # Ejecutar y esperar resultados
    results = job.apply_async()

    # Merge resultados
    return merge_batch_results(results.get())
```

### Fase 5: Análisis con OpenAI

#### 5.1 Llamada a Responses API
```python
def analyze_batch_with_openai(comments: List[str]) -> dict:
    """Analiza batch usando Responses API con Structured Outputs"""

    client = OpenAI()

    # Definir esquema de salida
    schema = {
        "type": "object",
        "properties": {
            "analysis": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer"},
                        "emotions": {
                            "type": "object",
                            "properties": {
                                "alegria": {"type": "number"},
                                "confianza": {"type": "number"},
                                "miedo": {"type": "number"},
                                "tristeza": {"type": "number"},
                                "enojo": {"type": "number"},
                                # ... más emociones
                            }
                        },
                        "churn_risk": {"type": "number"},
                        "pain_points": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "sentiment_score": {"type": "number"}
                    }
                }
            }
        }
    }

    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=ANALYSIS_PROMPT,
        input=format_comments_for_analysis(comments),
        text={
            "format": {
                "type": "json_schema",
                "schema": schema,
                "strict": True
            }
        }
    )

    return json.loads(response.output_text)
```

#### 5.2 Rate Limiting y Reintentos
```python
class RateLimiter:
    def __init__(self, max_rps: int = 8):
        self.max_rps = max_rps
        self.semaphore = asyncio.Semaphore(max_rps)
        self.window = []

    async def acquire(self):
        async with self.semaphore:
            now = time.time()
            # Ventana deslizante de 1 segundo
            self.window = [t for t in self.window if now - t < 1.0]

            if len(self.window) >= self.max_rps:
                sleep_time = 1.0 - (now - self.window[0])
                await asyncio.sleep(sleep_time)

            self.window.append(time.time())

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=4),
    retry=retry_if_exception_type((RateLimitError, APIError))
)
async def call_openai_with_retry(payload):
    await rate_limiter.acquire()
    return await openai_client.request(payload)
```

### Fase 6: Agregación de Resultados

#### 6.1 Merge de Batches
```python
def merge_batch_results(batch_results: List[dict]) -> dict:
    """Consolida resultados de múltiples batches"""

    merged = {
        'rows': [],
        'summary': {
            'total': 0,
            'emotions': defaultdict(float),
            'nps': {'promoters': 0, 'passives': 0, 'detractors': 0},
            'churn_risk_avg': 0,
            'pain_points': defaultdict(int)
        }
    }

    for batch in batch_results:
        merged['rows'].extend(batch['analysis'])

        # Agregar estadísticas
        for row in batch['analysis']:
            merged['summary']['total'] += 1

            # Acumular emociones
            for emotion, score in row['emotions'].items():
                merged['summary']['emotions'][emotion] += score

            # Acumular churn
            merged['summary']['churn_risk_avg'] += row['churn_risk']

            # Contar pain points
            for pain_point in row['pain_points']:
                merged['summary']['pain_points'][pain_point] += 1

    # Calcular promedios
    if merged['summary']['total'] > 0:
        n = merged['summary']['total']
        for emotion in merged['summary']['emotions']:
            merged['summary']['emotions'][emotion] /= n
        merged['summary']['churn_risk_avg'] /= n

    return merged
```

#### 6.2 Cálculo de Métricas Agregadas
```python
def calculate_aggregated_metrics(data: dict) -> dict:
    """Calcula métricas finales del análisis"""

    # NPS Score
    total = sum(data['summary']['nps'].values())
    if total > 0:
        nps_score = (
            (data['summary']['nps']['promoters'] -
             data['summary']['nps']['detractors']) / total * 100
        )
    else:
        nps_score = 0

    # Top Pain Points
    pain_points_sorted = sorted(
        data['summary']['pain_points'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    # Emotion dominante
    dominant_emotion = max(
        data['summary']['emotions'].items(),
        key=lambda x: x[1]
    )

    return {
        'nps_score': round(nps_score, 1),
        'top_pain_points': pain_points_sorted,
        'dominant_emotion': dominant_emotion,
        'high_churn_percentage': calculate_high_churn_percentage(data),
        'sentiment_distribution': calculate_sentiment_distribution(data)
    }
```

### Fase 7: Almacenamiento y Cache

#### 7.1 Persistencia en Redis
```python
def store_results(task_id: str, results: dict):
    """Almacena resultados con TTL"""

    # Serializar resultados
    serialized = json.dumps(results, cls=CustomJSONEncoder)

    # Guardar en Redis con TTL
    redis_client.setex(
        f"results:{task_id}",
        RESULTS_TTL_SECONDS,  # 24 horas default
        serialized
    )

    # Actualizar estado
    redis_client.hset(
        f"task:{task_id}",
        mapping={
            'status': 'completed',
            'progress': 100,
            'completed_at': datetime.utcnow().isoformat()
        }
    )
```

#### 7.2 Generación de Exports
```python
def generate_export_files(task_id: str, results: dict):
    """Genera archivos descargables"""

    # CSV detallado
    df_detailed = pd.DataFrame(results['rows'])
    csv_path = f"/tmp/{task_id}_detailed.csv"
    df_detailed.to_csv(csv_path, index=False)

    # Excel con múltiples hojas
    excel_path = f"/tmp/{task_id}_analysis.xlsx"
    with pd.ExcelWriter(excel_path) as writer:
        # Hoja 1: Resumen
        df_summary = pd.DataFrame([results['summary']])
        df_summary.to_excel(writer, sheet_name='Resumen', index=False)

        # Hoja 2: Detalle
        df_detailed.to_excel(writer, sheet_name='Detalle', index=False)

        # Hoja 3: Pain Points
        df_pain = pd.DataFrame(
            results['aggregated']['top_pain_points'],
            columns=['Pain Point', 'Frecuencia']
        )
        df_pain.to_excel(writer, sheet_name='Pain Points', index=False)

    return {
        'csv': csv_path,
        'excel': excel_path
    }
```

### Fase 8: Entrega de Resultados

#### 8.1 Polling de Estado
```javascript
// Frontend: Polling del progreso
const pollTaskStatus = async (taskId) => {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/status/${taskId}`);
    const data = await response.json();

    updateProgressBar(data.progress);
    updateStatusMessage(data.message);

    if (data.status === 'completed') {
      clearInterval(interval);
      await fetchResults(taskId);
    }

    if (data.status === 'failed') {
      clearInterval(interval);
      handleError(data.error);
    }
  }, 1000); // Poll cada segundo
};
```

#### 8.2 Renderizado de Visualizaciones
```javascript
// Frontend: Generación de gráficas
const renderCharts = (results) => {
  // Gráfica de emociones
  const emotionsChart = {
    type: 'bar',
    data: {
      labels: Object.keys(results.summary.emotions),
      values: Object.values(results.summary.emotions)
    },
    layout: {
      title: 'Distribución de Emociones',
      colorscale: 'Viridis'
    }
  };

  // NPS Gauge
  const npsGauge = {
    type: 'indicator',
    mode: 'gauge+number',
    value: results.aggregated.nps_score,
    gauge: {
      axis: { range: [-100, 100] },
      bar: { color: getNPSColor(results.aggregated.nps_score) },
      steps: [
        { range: [-100, 0], color: 'lightgray' },
        { range: [0, 50], color: 'gray' },
        { range: [50, 100], color: 'darkgray' }
      ]
    }
  };

  Plotly.newPlot('emotions-chart', emotionsChart);
  Plotly.newPlot('nps-gauge', npsGauge);
};
```

## Optimizaciones del Pipeline

### Paralelización
- Procesamiento simultáneo de batches
- Workers Celery concurrentes
- Async I/O donde sea posible

### Caching
- Cache de resultados frecuentes
- Memoización de cálculos costosos
- CDN para assets estáticos

### Compresión
- Gzip para respuestas API
- Compresión de archivos exportados
- Minificación de JSON responses

## Monitoreo del Pipeline

### Métricas por Fase
```python
PIPELINE_METRICS = {
    'upload': ['file_size', 'validation_time'],
    'normalization': ['rows_cleaned', 'invalid_rows'],
    'chunking': ['batch_count', 'avg_batch_size'],
    'analysis': ['api_calls', 'tokens_used', 'retry_count'],
    'aggregation': ['merge_time', 'metrics_calculated'],
    'storage': ['redis_write_time', 'export_generation_time'],
    'delivery': ['response_time', 'bandwidth_used']
}
```

### Alertas Configuradas
- Latencia > 10s para 1000 comentarios
- Error rate > 1%
- Queue depth > 100 tasks
- Redis memory > 80%
- OpenAI rate limit warnings

## Casos Edge y Manejo de Errores

### Archivo Vacío
```python
if df.empty:
    return {
        'error': 'Archivo sin datos válidos',
        'details': 'Verifique que el archivo contenga las columnas requeridas'
    }
```

### Timeout de OpenAI
```python
try:
    result = await call_openai_with_timeout(payload, timeout=30)
except TimeoutError:
    # Fallback a análisis parcial o retry
    return partial_analysis_fallback(batch)
```

### Memoria Insuficiente
```python
if get_available_memory() < MINIMUM_MEMORY_MB:
    # Reducir batch size dinámicamente
    adjusted_batch_size = max(10, current_batch_size // 2)
    return process_with_reduced_batch(data, adjusted_batch_size)
```

## Performance Benchmarks

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| 850 comentarios | <10s | 8.5s |
| 1200 comentarios | <15s | 12s |
| 2000 comentarios | <25s | 22s |
| 3000 comentarios | <40s | 35s |
| Concurrent tasks | 10 | 10 |
| Memory per task | <500MB | 350MB |
| API efficiency | >90% | 94% |