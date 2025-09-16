# Sistema de Detección de Emociones

## Visión General

El módulo de emociones implementa un sistema de análisis multidimensional que detecta 16 estados emocionales en comentarios de clientes, basado en el modelo de Plutchik adaptado para feedback empresarial.

## Las 16 Emociones

### Emociones Positivas (7)

#### 1. **Alegría** (Joy)
- **Indicadores**: Expresiones de felicidad, satisfacción, celebración
- **Keywords ES**: feliz, contento, genial, excelente, maravilloso
- **Keywords EN**: happy, glad, great, excellent, wonderful
- **Peso en NPS**: Alto impacto positivo

#### 2. **Confianza** (Trust)
- **Indicadores**: Seguridad en el servicio, lealtad, recomendación
- **Keywords ES**: confío, seguro, siempre, recomiendo, fiel
- **Keywords EN**: trust, reliable, always, recommend, loyal
- **Peso en Churn**: Reduce significativamente el riesgo

#### 3. **Anticipación** (Anticipation)
- **Indicadores**: Expectativa positiva, planes futuros con la marca
- **Keywords ES**: espero, próxima vez, volveré, ansioso por
- **Keywords EN**: looking forward, next time, will return, excited
- **Peso en Retención**: Indicador fuerte de continuidad

#### 4. **Sorpresa Positiva** (Positive Surprise)
- **Indicadores**: Superación de expectativas
- **Keywords ES**: sorprendido, no esperaba, increíble, wow
- **Keywords EN**: surprised, unexpected, amazing, wow
- **Peso en Viralidad**: Alta probabilidad de compartir

#### 5. **Amor** (Love)
- **Indicadores**: Conexión emocional profunda con la marca
- **Keywords ES**: amo, adoro, me encanta, lo mejor
- **Keywords EN**: love, adore, best thing ever
- **Peso en LTV**: Máximo valor de vida del cliente

#### 6. **Optimismo** (Optimism)
- **Indicadores**: Visión positiva del futuro con el servicio
- **Keywords ES**: mejorará, confío que, seguro que, esperanzado
- **Keywords EN**: will improve, confident, hopeful
- **Peso en Resiliencia**: Tolerancia a problemas menores

#### 7. **Admiración** (Admiration)
- **Indicadores**: Respeto y aprecio por la calidad
- **Keywords ES**: admiro, respeto, profesional, ejemplar
- **Keywords EN**: admire, respect, professional, exemplary
- **Peso en Advocacy**: Alta probabilidad de defensa de marca

### Emociones Negativas (7)

#### 8. **Miedo** (Fear)
- **Indicadores**: Preocupación, ansiedad sobre el servicio
- **Keywords ES**: temo, preocupado, inseguro, dudoso
- **Keywords EN**: afraid, worried, concerned, uncertain
- **Peso en Churn**: Aumenta riesgo moderadamente

#### 9. **Tristeza** (Sadness)
- **Indicadores**: Decepción, pérdida, desilusión
- **Keywords ES**: triste, decepcionado, lamentable, desilusionado
- **Keywords EN**: sad, disappointed, regret, let down
- **Peso en Satisfacción**: Impacto negativo directo

#### 10. **Enojo** (Anger)
- **Indicadores**: Frustración activa, irritación
- **Keywords ES**: enojado, furioso, harto, indignado, molesto
- **Keywords EN**: angry, furious, fed up, outraged, annoyed
- **Peso en Escalación**: Alta probabilidad de queja formal

#### 11. **Disgusto** (Disgust)
- **Indicadores**: Rechazo, repulsión hacia aspectos del servicio
- **Keywords ES**: asqueroso, repugnante, inaceptable, terrible
- **Keywords EN**: disgusting, revolting, unacceptable, awful
- **Peso en Viral Negativo**: Alta probabilidad de reviews negativos

#### 12. **Sorpresa Negativa** (Negative Surprise)
- **Indicadores**: Shock por problemas inesperados
- **Keywords ES**: no puedo creer, impactado, shock, inesperado
- **Keywords EN**: can't believe, shocked, unexpected problem
- **Peso en Confianza**: Erosiona confianza rápidamente

#### 13. **Vergüenza** (Shame)
- **Indicadores**: Sentimiento de humillación o exposición
- **Keywords ES**: avergonzado, humillado, ridículo, penoso
- **Keywords EN**: embarrassed, humiliated, ridiculous
- **Peso Social**: Reduce probabilidad de recomendación

#### 14. **Culpa** (Guilt)
- **Indicadores**: Auto-reproche por usar/no usar el servicio
- **Keywords ES**: culpable, debería haber, mi error, responsable
- **Keywords EN**: guilty, should have, my fault
- **Peso en Engagement**: Puede reducir uso del servicio

### Emociones Neutras (2)

#### 15. **Interés** (Interest)
- **Indicadores**: Curiosidad, engagement sin valencia clara
- **Keywords ES**: interesante, curioso, quiero saber, pregunto
- **Keywords EN**: interesting, curious, want to know, wondering
- **Peso en Conversión**: Oportunidad de engagement

#### 16. **Confusión** (Confusion)
- **Indicadores**: Falta de claridad, desorientación
- **Keywords ES**: confundido, no entiendo, poco claro, perdido
- **Keywords EN**: confused, don't understand, unclear, lost
- **Peso en UX**: Señala problemas de experiencia

## Algoritmo de Detección

### 1. Preprocesamiento

```python
def preprocess_comment(text: str) -> dict:
    """Preprocesa el comentario para análisis emocional"""
    return {
        'original': text,
        'normalized': normalize_text(text),
        'tokens': tokenize(text),
        'language': detect_language(text),
        'intensity_markers': extract_intensity_markers(text),
        'negations': detect_negations(text)
    }
```

### 2. Análisis Multi-Capa

```python
class EmotionAnalyzer:
    def analyze(self, comment: str) -> EmotionProfile:
        # Capa 1: Análisis léxico
        lexical_scores = self.lexical_analysis(comment)

        # Capa 2: Análisis contextual
        contextual_scores = self.contextual_analysis(comment)

        # Capa 3: Análisis de intensidad
        intensity_adjusted = self.adjust_for_intensity(
            lexical_scores,
            contextual_scores
        )

        # Capa 4: Normalización y validación
        final_scores = self.normalize_scores(intensity_adjusted)

        return EmotionProfile(final_scores)
```

### 3. Scoring y Normalización

```python
def calculate_emotion_scores(
    lexical: dict,
    contextual: dict,
    weights: dict
) -> dict:
    """Calcula scores finales de emociones"""
    scores = {}

    for emotion in EMOTIONS:
        # Combinar señales con pesos
        score = (
            lexical.get(emotion, 0) * weights['lexical'] +
            contextual.get(emotion, 0) * weights['contextual']
        )

        # Aplicar sigmoid para rango [0,1]
        scores[emotion] = 1 / (1 + math.exp(-score))

    return scores
```

## Reglas de Negocio

### Coexistencia de Emociones

```python
EMOTION_COMPATIBILITY = {
    'alegria': {
        'compatible': ['confianza', 'optimismo', 'amor'],
        'incompatible': ['tristeza', 'enojo'],
        'neutral': ['interes', 'confusion']
    },
    'enojo': {
        'compatible': ['disgusto', 'miedo'],
        'incompatible': ['alegria', 'amor'],
        'amplifies': ['churn_risk']
    }
}
```

### Umbrales de Detección

```python
DETECTION_THRESHOLDS = {
    'very_low': 0.0 - 0.2,
    'low': 0.2 - 0.4,
    'moderate': 0.4 - 0.6,
    'high': 0.6 - 0.8,
    'very_high': 0.8 - 1.0
}

def get_emotion_intensity(score: float) -> str:
    """Categoriza la intensidad emocional"""
    if score < 0.2:
        return 'very_low'
    elif score < 0.4:
        return 'low'
    elif score < 0.6:
        return 'moderate'
    elif score < 0.8:
        return 'high'
    else:
        return 'very_high'
```

## Patrones de Detección

### Patrones Léxicos

```python
EMOTION_LEXICONS = {
    'es': {
        'alegria': {
            'strong': ['feliz', 'encantado', 'maravilloso'],
            'moderate': ['bien', 'bueno', 'agradable'],
            'weak': ['ok', 'normal', 'correcto']
        },
        'enojo': {
            'strong': ['furioso', 'indignado', 'inaceptable'],
            'moderate': ['molesto', 'frustrado', 'mal'],
            'weak': ['incómodo', 'no me gustó']
        }
    },
    'en': {
        'alegria': {
            'strong': ['happy', 'delighted', 'wonderful'],
            'moderate': ['good', 'nice', 'pleasant'],
            'weak': ['ok', 'fine', 'alright']
        }
    }
}
```

### Modificadores de Intensidad

```python
INTENSITY_MODIFIERS = {
    'amplifiers': {
        'es': ['muy', 'super', 'extremadamente', 'totalmente'],
        'en': ['very', 'super', 'extremely', 'totally']
    },
    'diminishers': {
        'es': ['poco', 'algo', 'ligeramente', 'apenas'],
        'en': ['slightly', 'somewhat', 'barely', 'little']
    },
    'negators': {
        'es': ['no', 'nunca', 'nada', 'ningún'],
        'en': ['not', 'never', 'nothing', 'none']
    }
}
```

## Integración con Métricas

### Impacto en NPS

```python
def emotion_to_nps_impact(emotions: dict) -> float:
    """Calcula el impacto emocional en NPS"""
    positive_weight = sum(
        emotions.get(e, 0) * POSITIVE_NPS_WEIGHTS[e]
        for e in POSITIVE_EMOTIONS
    )

    negative_weight = sum(
        emotions.get(e, 0) * NEGATIVE_NPS_WEIGHTS[e]
        for e in NEGATIVE_EMOTIONS
    )

    return positive_weight - negative_weight
```

### Predicción de Churn

```python
def emotion_churn_correlation(emotions: dict) -> float:
    """Correlaciona emociones con riesgo de churn"""
    churn_score = 0

    # Factores de riesgo
    churn_score += emotions.get('enojo', 0) * 0.3
    churn_score += emotions.get('disgusto', 0) * 0.25
    churn_score += emotions.get('miedo', 0) * 0.15
    churn_score += emotions.get('tristeza', 0) * 0.2

    # Factores protectores
    churn_score -= emotions.get('confianza', 0) * 0.4
    churn_score -= emotions.get('amor', 0) * 0.35
    churn_score -= emotions.get('optimismo', 0) * 0.2

    return max(0, min(1, churn_score))
```

## Casos Especiales

### Sarcasmo e Ironía

```python
def detect_sarcasm(text: str, emotions: dict) -> bool:
    """Detecta posible sarcasmo en el texto"""
    sarcasm_indicators = [
        # Discrepancia entre palabras positivas y puntuación baja
        emotions['alegria'] > 0.5 and 'pero' in text,

        # Uso de comillas en palabras positivas
        bool(re.search(r'"[^"]*(?:bueno|excelente|genial)[^"]*"', text)),

        # Patrones específicos
        bool(re.search(r'(claro|obvio|por supuesto).*\!+', text))
    ]

    return sum(sarcasm_indicators) >= 2
```

### Contexto Cultural

```python
CULTURAL_ADJUSTMENTS = {
    'es': {
        'expression_intensity': 1.1,  # Mayor expresividad
        'negative_threshold': 0.45,   # Umbral más alto para negatividad
    },
    'en': {
        'expression_intensity': 0.9,  # Menor expresividad
        'negative_threshold': 0.35,   # Umbral más bajo
    }
}
```

## Visualización de Emociones

### Radar Chart

```python
def create_emotion_radar(emotions: dict) -> dict:
    """Crea configuración para radar chart de emociones"""
    return {
        'type': 'scatterpolar',
        'r': [emotions.get(e, 0) for e in EMOTIONS],
        'theta': EMOTIONS,
        'fill': 'toself',
        'name': 'Perfil Emocional'
    }
```

### Heatmap Temporal

```python
def create_emotion_heatmap(emotion_series: List[dict]) -> dict:
    """Crea heatmap de evolución emocional"""
    return {
        'type': 'heatmap',
        'z': [[row[emotion] for emotion in EMOTIONS]
              for row in emotion_series],
        'x': EMOTIONS,
        'y': list(range(len(emotion_series))),
        'colorscale': 'RdYlGn'
    }
```

## Testing y Validación

### Test Cases

```python
EMOTION_TEST_CASES = [
    {
        'input': "Estoy muy feliz con el servicio, superó mis expectativas",
        'expected': {
            'alegria': (0.7, 1.0),
            'sorpresa_positiva': (0.5, 0.8),
            'confianza': (0.4, 0.7)
        }
    },
    {
        'input': "Terrible experiencia, nunca volveré",
        'expected': {
            'disgusto': (0.6, 0.9),
            'enojo': (0.5, 0.8),
            'churn_risk': (0.8, 1.0)
        }
    }
]
```

### Métricas de Calidad

```python
def evaluate_emotion_detection(
    predicted: dict,
    ground_truth: dict
) -> dict:
    """Evalúa calidad de detección emocional"""
    return {
        'mae': mean_absolute_error(predicted, ground_truth),
        'correlation': pearson_correlation(predicted, ground_truth),
        'top3_accuracy': top_k_accuracy(predicted, ground_truth, k=3)
    }
```

## Optimización de Performance

### Caching de Lexicons

```python
@lru_cache(maxsize=10000)
def get_emotion_keywords(language: str, emotion: str) -> set:
    """Cache de keywords por idioma y emoción"""
    return set(EMOTION_LEXICONS[language][emotion])
```

### Procesamiento Batch

```python
def batch_emotion_analysis(
    comments: List[str],
    batch_size: int = 50
) -> List[dict]:
    """Análisis eficiente en batch"""
    # Vectorización de features
    features = vectorize_comments(comments)

    # Procesamiento paralelo
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(
            analyze_emotion_vector,
            features,
            chunksize=batch_size
        )

    return list(results)
```

## Roadmap de Mejoras

### Corto Plazo
- [ ] Mejorar detección de sarcasmo
- [ ] Añadir más idiomas (pt, fr)
- [ ] Calibración por industria

### Mediano Plazo
- [ ] Modelo de deep learning propio
- [ ] Análisis de emociones mixtas
- [ ] Tracking de evolución emocional

### Largo Plazo
- [ ] Análisis multimodal (texto + voz)
- [ ] Predicción de emociones futuras
- [ ] Personalización por segmento de cliente