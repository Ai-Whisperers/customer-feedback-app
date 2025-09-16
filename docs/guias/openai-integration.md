# Integración OpenAI - Responses API

## Introducción

Este documento detalla la integración con la **Responses API** de OpenAI, la nueva generación de APIs que reemplaza a Chat Completions con mejor soporte para structured outputs y reasoning models.

## Configuración del Cliente

### Instalación
```bash
pip install openai>=1.0.0
```

### Inicialización
```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    # Opcional: para Azure OpenAI
    base_url=os.getenv('OPENAI_BASE_URL')
)
```

## Responses API vs Chat Completions

### Principales Diferencias

| Feature | Chat Completions | Responses API |
|---------|-----------------|---------------|
| Formato Input | `messages` | `input` + `instructions` |
| Formato Output | `choices[].message` | `output[]` items tipados |
| Structured Output | `response_format` | `text.format` |
| Function Calling | Legacy format | Nuevo formato mejorado |
| Storage | Opcional | Por defecto |
| Reasoning | Limitado | Nativo con items de reasoning |
| Estado | Stateless | Soporta `previous_response_id` |

### Migración de Código

**Antes (Chat Completions):**
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "Eres un asistente"},
        {"role": "user", "content": "Analiza este texto"}
    ],
    response_format={"type": "json_object"}
)
```

**Ahora (Responses API):**
```python
response = client.responses.create(
    model="gpt-4o-mini",
    instructions="Eres un asistente de análisis",
    input="Analiza este texto",
    text={
        "format": {
            "type": "json_schema",
            "schema": analysis_schema,
            "strict": True
        }
    }
)
```

## Structured Outputs con JSON Schema

### Definición del Schema

```python
def get_analysis_schema():
    """Define el esquema JSON para análisis de comentarios"""
    return {
        "type": "object",
        "properties": {
            "comments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "integer",
                            "description": "Índice del comentario"
                        },
                        "emotions": {
                            "type": "object",
                            "properties": {
                                # Emociones positivas
                                "alegria": {"type": "number", "minimum": 0, "maximum": 1},
                                "confianza": {"type": "number", "minimum": 0, "maximum": 1},
                                "anticipacion": {"type": "number", "minimum": 0, "maximum": 1},
                                "sorpresa_positiva": {"type": "number", "minimum": 0, "maximum": 1},
                                "amor": {"type": "number", "minimum": 0, "maximum": 1},
                                "optimismo": {"type": "number", "minimum": 0, "maximum": 1},
                                "admiracion": {"type": "number", "minimum": 0, "maximum": 1},

                                # Emociones negativas
                                "miedo": {"type": "number", "minimum": 0, "maximum": 1},
                                "tristeza": {"type": "number", "minimum": 0, "maximum": 1},
                                "enojo": {"type": "number", "minimum": 0, "maximum": 1},
                                "disgusto": {"type": "number", "minimum": 0, "maximum": 1},
                                "sorpresa_negativa": {"type": "number", "minimum": 0, "maximum": 1},
                                "verguenza": {"type": "number", "minimum": 0, "maximum": 1},
                                "culpa": {"type": "number", "minimum": 0, "maximum": 1},

                                # Emociones neutras
                                "interes": {"type": "number", "minimum": 0, "maximum": 1},
                                "confusion": {"type": "number", "minimum": 0, "maximum": 1}
                            },
                            "required": ["alegria", "confianza", "miedo", "tristeza", "enojo"],
                            "additionalProperties": False
                        },
                        "churn_risk": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Probabilidad de abandono (0-1)"
                        },
                        "pain_points": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "minLength": 2,
                                "maxLength": 50
                            },
                            "maxItems": 5,
                            "description": "Principales problemas mencionados"
                        },
                        "sentiment": {
                            "type": "string",
                            "enum": ["muy_positivo", "positivo", "neutral", "negativo", "muy_negativo"]
                        },
                        "language": {
                            "type": "string",
                            "enum": ["es", "en"]
                        }
                    },
                    "required": ["id", "emotions", "churn_risk", "pain_points", "sentiment", "language"],
                    "additionalProperties": False
                }
            },
            "batch_summary": {
                "type": "object",
                "properties": {
                    "total_analyzed": {"type": "integer"},
                    "avg_sentiment_score": {"type": "number"},
                    "main_concerns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": 10
                    }
                },
                "required": ["total_analyzed", "avg_sentiment_score", "main_concerns"],
                "additionalProperties": False
            }
        },
        "required": ["comments", "batch_summary"],
        "additionalProperties": False
    }
```

### Implementación de la Llamada

```python
class OpenAIAnalyzer:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = OpenAI()
        self.model = model
        self.schema = get_analysis_schema()

    async def analyze_batch(
        self,
        comments: List[str],
        context: Optional[str] = None
    ) -> dict:
        """Analiza un batch de comentarios usando Responses API"""

        # Preparar instrucciones
        instructions = self._build_instructions(context)

        # Formatear input
        input_text = self._format_comments_input(comments)

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=instructions,
                input=input_text,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "comment_analysis",
                        "schema": self.schema,
                        "strict": True
                    }
                },
                temperature=0.3,  # Baja para consistencia
                max_output_tokens=4000
            )

            # Parse resultado
            return json.loads(response.output_text)

        except Exception as e:
            logger.error(f"Error in OpenAI analysis: {e}")
            raise

    def _build_instructions(self, context: Optional[str]) -> str:
        """Construye las instrucciones del sistema"""
        base_instructions = """
        Eres un experto en análisis de sentimientos y feedback de clientes.
        Tu tarea es analizar comentarios de clientes y extraer:

        1. EMOCIONES: Asigna probabilidades (0-1) a cada emoción
           - La suma NO debe ser 1, pueden coexistir múltiples emociones
           - Sé preciso y considera matices sutiles

        2. CHURN RISK: Evalúa probabilidad de abandono (0-1) basándote en:
           - Tono general del comentario
           - Menciones de competencia
           - Nivel de frustración expresado
           - Intención de cancelar o cambiar

        3. PAIN POINTS: Identifica problemas específicos mencionados
           - Usa palabras clave concisas
           - Máximo 5 por comentario
           - En el idioma original del comentario

        4. SENTIMENT: Clasifica el sentimiento general
           - Considera el contexto completo
           - No solo palabras individuales

        5. LANGUAGE: Detecta si el comentario está en español (es) o inglés (en)

        IMPORTANTE:
        - Mantén objetividad y precisión
        - No inventes información no presente en el texto
        - Respeta el formato JSON Schema exactamente
        """

        if context:
            base_instructions += f"\n\nContexto adicional: {context}"

        return base_instructions

    def _format_comments_input(self, comments: List[str]) -> str:
        """Formatea los comentarios para el análisis"""
        formatted = []
        for idx, comment in enumerate(comments):
            formatted.append(f"[{idx}] {comment}")

        return "\n\n".join(formatted)
```

## Prompting Avanzado

### Prompt Engineering para Análisis

```python
ANALYSIS_PROMPT_TEMPLATE = """
Analiza los siguientes {count} comentarios de clientes.

CONTEXTO:
- Empresa: {company_context}
- Período: {time_period}
- Segmento: {segment}

COMENTARIOS A ANALIZAR:
{comments}

INSTRUCCIONES ESPECÍFICAS:
1. Para emociones ambiguas, usa el contexto para desambiguar
2. Si mencionan precio/costo, aumenta ligeramente churn_risk
3. Pain points deben ser específicos (ej: "tiempo_espera_largo" no solo "espera")
4. Detecta sarcasmo y ajusta sentiment apropiadamente
5. Identifica menciones de competidores para churn_risk

Responde ÚNICAMENTE con el JSON estructurado según el schema proporcionado.
"""
```

### Few-Shot Examples

```python
def add_few_shot_examples(instructions: str) -> str:
    """Agrega ejemplos para mejorar la precisión"""
    examples = """
    EJEMPLOS DE ANÁLISIS CORRECTO:

    Comentario: "El servicio fue pésimo, tardaron 2 horas y la comida llegó fría"
    Análisis: {
        "emotions": {"enojo": 0.8, "frustración": 0.7, "decepción": 0.6},
        "churn_risk": 0.85,
        "pain_points": ["tiempo_entrega_excesivo", "comida_fria"],
        "sentiment": "muy_negativo"
    }

    Comentario: "Excelente atención, volveré pronto!"
    Análisis: {
        "emotions": {"alegria": 0.9, "confianza": 0.8, "satisfacción": 0.9},
        "churn_risk": 0.05,
        "pain_points": [],
        "sentiment": "muy_positivo"
    }
    """
    return instructions + examples
```

## Function Calling con Responses API

### Definición de Tools

```python
tools = [
    {
        "type": "function",
        "name": "analyze_sentiment",
        "description": "Analiza el sentimiento de un texto",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Texto a analizar"
                },
                "language": {
                    "type": "string",
                    "enum": ["es", "en"],
                    "description": "Idioma del texto"
                }
            },
            "required": ["text", "language"],
            "additionalProperties": False
        },
        "strict": True
    },
    {
        "type": "function",
        "name": "extract_entities",
        "description": "Extrae entidades nombradas del texto",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "entity_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["producto", "servicio", "persona", "lugar"]
                    }
                }
            },
            "required": ["text", "entity_types"],
            "additionalProperties": False
        },
        "strict": True
    }
]
```

### Manejo de Tool Calls

```python
async def handle_tool_calls(response):
    """Procesa las llamadas a funciones del modelo"""
    tool_outputs = []

    for item in response.output:
        if item.type == "function_call":
            result = await execute_function(
                item.name,
                json.loads(item.arguments)
            )

            tool_outputs.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result)
            })

    return tool_outputs

async def execute_function(name: str, args: dict):
    """Ejecuta la función solicitada"""
    if name == "analyze_sentiment":
        return analyze_sentiment(**args)
    elif name == "extract_entities":
        return extract_entities(**args)
    else:
        raise ValueError(f"Unknown function: {name}")
```

## Optimización y Best Practices

### 1. Control de Tokens

```python
def estimate_tokens(text: str) -> int:
    """Estima tokens para controlar costos"""
    # Aproximación: 1 token ≈ 4 caracteres en español/inglés
    return len(text) // 4

def optimize_batch_size(comments: List[str], max_tokens: int = 4000) -> List[List[str]]:
    """Optimiza el tamaño de batch basado en tokens"""
    batches = []
    current_batch = []
    current_tokens = 0

    for comment in comments:
        comment_tokens = estimate_tokens(comment)

        if current_tokens + comment_tokens > max_tokens:
            batches.append(current_batch)
            current_batch = [comment]
            current_tokens = comment_tokens
        else:
            current_batch.append(comment)
            current_tokens += comment_tokens

    if current_batch:
        batches.append(current_batch)

    return batches
```

### 2. Rate Limiting

```python
from asyncio import Semaphore
import time

class OpenAIRateLimiter:
    def __init__(self, requests_per_minute: int = 500):
        self.rpm = requests_per_minute
        self.semaphore = Semaphore(requests_per_minute // 60)
        self.request_times = []

    async def acquire(self):
        """Adquiere permiso para hacer request"""
        await self.semaphore.acquire()

        # Sliding window rate limiting
        now = time.time()
        minute_ago = now - 60

        # Limpiar requests viejos
        self.request_times = [
            t for t in self.request_times
            if t > minute_ago
        ]

        # Verificar límite
        if len(self.request_times) >= self.rpm:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

        self.request_times.append(time.time())

    def release(self):
        """Libera el semáforo"""
        self.semaphore.release()
```

### 3. Error Handling

```python
class OpenAIErrorHandler:
    @staticmethod
    def handle_api_error(error):
        """Maneja errores específicos de OpenAI"""
        if isinstance(error, openai.RateLimitError):
            # Esperar y reintentar
            return {"action": "retry", "wait": 60}

        elif isinstance(error, openai.APIError):
            # Error del servidor
            if error.status_code >= 500:
                return {"action": "retry", "wait": 5}

        elif isinstance(error, openai.InvalidRequestError):
            # Request inválido - no reintentar
            logger.error(f"Invalid request: {error}")
            return {"action": "fail"}

        elif isinstance(error, openai.AuthenticationError):
            # Error de autenticación - fatal
            logger.critical("Authentication failed")
            return {"action": "fatal"}

        return {"action": "retry", "wait": 1}
```

### 4. Caching Inteligente

```python
class ResponseCache:
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl

    def get_cache_key(self, comments: List[str], model: str) -> str:
        """Genera key única para el cache"""
        content = "".join(sorted(comments))
        return hashlib.md5(f"{content}:{model}".encode()).hexdigest()

    def get(self, comments: List[str], model: str) -> Optional[dict]:
        """Obtiene resultado del cache si existe"""
        key = self.get_cache_key(comments, model)

        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['data']

        return None

    def set(self, comments: List[str], model: str, data: dict):
        """Guarda resultado en cache"""
        key = self.get_cache_key(comments, model)
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
```

## Monitoreo y Métricas

### Tracking de Uso

```python
class OpenAIUsageTracker:
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'errors': 0,
            'cache_hits': 0
        }

    def track_request(self, response):
        """Registra métricas de un request"""
        self.metrics['total_requests'] += 1

        if hasattr(response, 'usage'):
            tokens = response.usage.total_tokens
            self.metrics['total_tokens'] += tokens

            # Calcular costo (ejemplo para gpt-4o-mini)
            cost = (tokens / 1000) * 0.0001  # $0.0001 per 1K tokens
            self.metrics['total_cost'] += cost

    def get_summary(self) -> dict:
        """Obtiene resumen de métricas"""
        return {
            **self.metrics,
            'avg_tokens_per_request': (
                self.metrics['total_tokens'] / max(1, self.metrics['total_requests'])
            ),
            'error_rate': (
                self.metrics['errors'] / max(1, self.metrics['total_requests'])
            ),
            'cache_hit_rate': (
                self.metrics['cache_hits'] / max(1, self.metrics['total_requests'])
            )
        }
```

## Testing de Integración

### Mock para Testing

```python
class MockOpenAIClient:
    """Mock client para testing sin gastar tokens"""

    def __init__(self):
        self.responses = self._load_mock_responses()

    def responses_create(self, **kwargs):
        """Simula response.create"""
        # Retorna respuesta mock basada en input
        return self._generate_mock_response(kwargs.get('input'))

    def _generate_mock_response(self, input_text):
        """Genera respuesta mock realista"""
        return {
            "output_text": json.dumps({
                "comments": [
                    {
                        "id": 0,
                        "emotions": {
                            "alegria": 0.5,
                            "confianza": 0.3,
                            "miedo": 0.1
                        },
                        "churn_risk": 0.2,
                        "pain_points": ["test_issue"],
                        "sentiment": "positivo",
                        "language": "es"
                    }
                ],
                "batch_summary": {
                    "total_analyzed": 1,
                    "avg_sentiment_score": 0.7,
                    "main_concerns": ["test_issue"]
                }
            })
        }
```

## Migración Futura

### Preparación para GPT-5

```python
class ModelVersionManager:
    """Gestiona transición entre versiones de modelos"""

    MODELS = {
        'stable': 'gpt-4o-mini',
        'experimental': 'gpt-4o-2024-08-06',
        'future': 'gpt-5'  # Cuando esté disponible
    }

    def get_model(self, tier: str = 'stable') -> str:
        """Obtiene modelo según tier"""
        return self.MODELS.get(tier, self.MODELS['stable'])

    def supports_feature(self, model: str, feature: str) -> bool:
        """Verifica si modelo soporta feature"""
        feature_matrix = {
            'gpt-4o-mini': ['structured_outputs', 'function_calling'],
            'gpt-4o-2024-08-06': ['structured_outputs', 'function_calling', 'reasoning'],
            'gpt-5': ['structured_outputs', 'function_calling', 'reasoning', 'multimodal']
        }
        return feature in feature_matrix.get(model, [])
```