# Evaluación RAG con RAGAS

Este directorio contiene la implementación completa de evaluación del sistema RAG utilizando RAGAS (RAG Assessment).

## Archivos Principales

### `evaluate_ragas.py`
Script principal que implementa toda la evaluación RAG con RAGAS. Incluye:
- Carga del dataset de 64 preguntas
- Cliente HTTP para la API RAG existente
- Configuración de RAGAS con Mistral como LLM evaluador
- Procesamiento por batches
- Cálculo de métricas: faithfulness, answer_relevancy, context_precision, context_recall, answer_correctness
- Generación de reportes detallados
- Exportación a CSV/JSON

### `api_rag.py`
API FastAPI existente que implementa el sistema RAG bilingüe (inglés KB → español respuestas).

### `data/evaluation_dataset.jsonl`
Dataset con 64 preguntas de evaluación en 6 tipos:
- **exactitud_fidelidad**: Preguntas sobre información específica y precisa
- **negaciones_contradicciones**: Preguntas que requieren identificar información incorrecta
- **desambiguacion**: Preguntas que requieren clarificar términos ambiguos
- **adversariales_seguridad**: Preguntas diseñadas para probar la robustez del sistema
- **contexto_incompleto**: Preguntas sobre información no disponible en el contexto
- **robustez_reformulaciones**: Preguntas con diferentes formulaciones del mismo concepto

## Uso

### Opción 1: Script de inicio automático
```bash
cd src/evaluation
python start_evaluation.py
```

### Opción 2: Ejecución manual

1. **Iniciar la API RAG** (en una terminal):
```bash
cd src/evaluation
python api_rag.py
```

2. **Ejecutar la evaluación** (en otra terminal):
```bash
cd src/evaluation
python evaluate_ragas.py
```

### Opción 3: Prueba de componentes
```bash
cd src/evaluation
python test_evaluation.py
```

## Requisitos

### Servicios necesarios
- **Qdrant**: Base de datos vectorial (puerto 6333)
- **Ollama**: Modelo de embeddings (puerto 11434)
- **Mistral API**: LLM para evaluación (configurado en .env)

### Variables de entorno
```bash
MISTRAL_API_KEY=tu_api_key_aqui
```

## Métricas Evaluadas

### 1. Faithfulness (Fidelidad)
Mide qué tan fiel es la respuesta al contexto proporcionado. Valores altos indican que la respuesta está bien fundamentada en el contexto.

### 2. Answer Relevancy (Relevancia de la Respuesta)
Evalúa qué tan relevante es la respuesta para la pregunta formulada.

### 3. Context Precision (Precisión del Contexto)
Mide qué tan preciso es el contexto recuperado para responder la pregunta.

### 4. Context Recall (Recuperación del Contexto)
Evalúa qué tan completo es el contexto recuperado en relación con la información necesaria.

### 5. Answer Correctness (Correctitud de la Respuesta)
Combina faithfulness y answer_relevancy para evaluar la calidad general de la respuesta.

## Resultados

Los resultados se guardan en el directorio `evaluation_results/` con timestamp:

- `evaluation_results_YYYYMMDD_HHMMSS.csv`: Resultados detallados en CSV
- `evaluation_results_YYYYMMDD_HHMMSS.json`: Resultados en formato JSON
- `evaluation_report_YYYYMMDD_HHMMSS.txt`: Reporte detallado en texto
- `evaluation_ragas.log`: Log de la evaluación

## Análisis de Resultados

El reporte incluye:

### Métricas Generales
- Promedio de todas las métricas
- Tiempo promedio de respuesta de la API
- Estadísticas de éxito/fallo

### Métricas por Tipo de Pregunta
- Análisis detallado por cada categoría de pregunta
- Identificación de patrones de fallo
- Comparación entre tipos de pregunta

### Casos Problemáticos
- Preguntas con scores bajos
- Errores encontrados
- Análisis de causas de fallo

### Recomendaciones
- Sugerencias específicas para mejorar el sistema
- Identificación de áreas de mejora
- Acciones recomendadas

## Configuración Avanzada

### Tamaño de Batch
El script procesa las preguntas en batches para evitar sobrecargar la API. El tamaño por defecto es 3, pero se puede modificar:

```python
evaluator.run_evaluation(batch_size=5)  # Cambiar tamaño de batch
```

### Timeouts
- API timeout: 30 segundos
- Evaluación timeout: Configurado por RAGAS
- Pausa entre preguntas: 1 segundo

### Logging
El sistema genera logs detallados en `evaluation_ragas.log` para debugging y monitoreo.

## Troubleshooting

### Error: "API no disponible"
- Verificar que Qdrant esté funcionando en puerto 6333
- Verificar que Ollama esté funcionando en puerto 11434
- Iniciar la API RAG con `python api_rag.py`

### Error: "MISTRAL_API_KEY no configurada"
- Configurar la variable de entorno en el archivo `.env`
- Verificar que la API key sea válida

### Error: "Dataset no encontrado"
- Verificar que `data/evaluation_dataset.jsonl` exista
- Verificar que el archivo contenga datos válidos en formato JSON Lines

### Error: "Timeout en consulta API"
- Verificar que la API RAG esté respondiendo correctamente
- Aumentar el timeout si es necesario
- Verificar la conectividad de red

## Estructura del Dataset

Cada línea del dataset debe tener el formato:
```json
{"type": "tipo_pregunta", "query": "pregunta", "answer": "respuesta_esperada"}
```

Donde:
- `type`: Tipo de pregunta (exactitud_fidelidad, negaciones_contradicciones, etc.)
- `query`: Pregunta a evaluar
- `answer`: Respuesta esperada (ground truth)

## Contribuciones

Para agregar nuevas preguntas de evaluación:
1. Editar `data/evaluation_dataset.jsonl`
2. Agregar una línea por pregunta en formato JSON
3. Ejecutar la evaluación para verificar que funcione

Para modificar las métricas evaluadas:
1. Editar la lista `self.metrics` en `evaluate_ragas.py`
2. Asegurar que las métricas sean compatibles con RAGAS
3. Actualizar la generación de reportes si es necesario
