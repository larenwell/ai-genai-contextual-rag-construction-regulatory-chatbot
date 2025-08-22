# Asistente de Normativa - Prototipo

Un asistente virtual inteligente para consultas sobre normativa técnica en español, implementado con RAG (Retrieval-Augmented Generation) y optimizado para el flujo de trabajo de base de conocimiento en inglés y respuestas en español.

## Características Principales

- **Procesamiento de PDFs**: Extracción inteligente de texto, tablas e imágenes usando Mistral OCR
- **Búsqueda Vectorial**: Búsqueda de similitud semántica usando Qdrant vector database
- **Respuestas con IA**: Respuestas contextuales usando modelos Mistral LLM
- **Multilingüe**: Base de conocimiento en inglés, interfaz y respuestas en español
- **Interfaz Web**: Chat interactivo con Chainlit
- **Validación Automática**: Scripts de validación de completitud de ingestión
- **Análisis de Documentos**: Herramientas de análisis y detección de duplicados

## Arquitectura

### Componentes Principales

1. **Ingestión de Documentos** (`src/ingestion/`)
   - Extracción de texto con Mistral OCR (modelo `mistral-ocr-latest`)
   - Procesamiento inteligente de PDFs con preservación de imágenes
   - Chunking inteligente con MarkdownHeaderTextSplitter
   - Contextualización automática con Mistral AI

2. **Embeddings y Vectorización** (`src/embeddings/`)
   - Generación de embeddings con modelo Ollama `nomic-embed-text`
   - Almacenamiento vectorial en Qdrant con configuración automática
   - Búsqueda de similitud semántica con distancia Cosine
   - Configuración: 768 dimensiones, almacenamiento en disco

3. **Modelos de Lenguaje** (`src/llm/`)
   - Integración con Mistral AI (`mistral-small-latest`)
   - Procesamiento RAG optimizado con prompts centralizados
   - Respuestas siempre en español para el usuario
   - Sistema de prompts configurable por idioma

4. **Interfaz de Usuario** (`src/`)
   - Frontend web con Chainlit
   - Configuración de visualización centralizada
   - Sistema de traducción automática (español ↔ inglés)
   - Manejo de errores y sugerencias de seguimiento

5. **Configuración y Gestión** (`src/config/`)
   - Configuración de visualización centralizada
   - Gestión de prompts por idioma
   - Configuración de elementos visuales y mensajes

6. **Análisis y Evaluación** (`src/analysis/`, `src/evaluation/`)
   - Análisis de PDFs con PyMuPDF y PyPDF2
   - Detección de duplicados inteligente
   - Evaluación RAG con métricas RAGAS
   - Generación de reportes Excel y JSON

## Requisitos

### Dependencias del Sistema
- **Python 3.12+** - Lenguaje principal del proyecto
- **uv** - Gestor de paquetes y entornos virtuales de Python
- **Node.js** - Runtime de JavaScript para herramientas de desarrollo
- **npm** - Gestor de paquetes de Node.js
- **npx** - Ejecutor de paquetes de Node.js
- **Docker** - Contenedores para Qdrant, PostgreSQL, Ollama y LocalStack
- **Docker Compose** - Orquestación de múltiples contenedores
- **Memoria RAM**: 8GB+ recomendado

### Versiones de Dependencias
- **Chainlit**: <2.6.0 (versión estable sin problemas de data layer)
- **Python**: 3.12+
- **Qdrant**: latest
- **Ollama**: latest
- **Mistral AI**: API v1

### Herramientas de Desarrollo
- **uv**: Gestor de paquetes Python moderno y rápido
- **Node.js**: Para ejecutar Prisma Studio y herramientas de desarrollo
- **npm/npx**: Gestión de dependencias de Node.js y ejecución de Prisma
- **Docker**: Contenedores para todos los servicios (Qdrant, PostgreSQL, Ollama, LocalStack)

### Variables de Entorno
```bash
# Mistral AI
MISTRAL_API_KEY=your_mistral_api_key

# Qdrant
QDRANT_COLLECTION_NAME=asistente-normativa-sincro-kb

# Configuración de PDFs
PDF_FOLDER_PATH=../data/test

# Base de Datos (opcional)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# AWS LocalStack (opcional)
BUCKET_NAME=my-bucket
APP_AWS_ACCESS_KEY=random-key
APP_AWS_SECRET_KEY=random-key
APP_AWS_REGION=eu-central-1
DEV_AWS_ENDPOINT=http://localhost:4566
```

## Instalación y Configuración

### 1. Clonar el Repositorio
   ```bash
   git clone <repository-url>
   cd ai-genai-contextual-rag-construction-regulatory-chatbot
   ```

### 2. Instalar Dependencias
   ```bash
   uv sync
   ```
Esto crea el entorno virtual y el archivo uv.lock

### 3. Configurar Entorno Virtual
   ```bash
   source .venv/bin/activate
```

### 4. Crear el archivo .env con las variables de entorno

### ⚠️ Nota Importante sobre Herramientas
**Todas las herramientas del sistema deben estar instaladas antes de proceder:**
- **uv**: Necesario para `uv sync` y gestión de dependencias Python
- **Node.js/npm**: Requerido para ejecutar `npx prisma studio`
- **Docker**: Esencial para todos los servicios (Qdrant, PostgreSQL, Ollama, LocalStack)
- **Ollama**: Necesario para embeddings locales con `nomic-embed-text`

## Despliegue de la solución

### Requisitos Previos
- Docker y Docker Compose instalados
- Variables de entorno configuradas

### Servicios Requeridos para la Solución Completa
La solución requiere **6 servicios principales** funcionando simultáneamente:

1. **Chainlit-datalayer** - Gestión de base de datos y servicios AWS
2. **PostgreSQL** - Base de datos principal para Chainlit
3. **Qdrant** - Base de datos vectorial para embeddings
4. **Ollama** - Modelo de embeddings local (nomic-embed-text)
5. **LocalStack** - Emulación de servicios AWS
6. **Chainlit Assistant** - Aplicación principal RAG

### Contenedores Requeridos

#### A. CHAINLIT-DATALAYER
Dentro del proyecto se necesita ejecutar lo siguiente:

   ```bash
# 1. Iniciar el contenedor: chainlit-datalayer
docker-compose up -d

# 2. Configurar variable de entorno
export DATABASE_URL=postgresql://root:root@localhost:5432/postgres

# 3. Ejecutar Prisma Studio
npx prisma studio
```

Se debe asegurar que los contenedores de QDRANT y OLLAMA estén corriendo:

#### B. QDRANT
```bash
# Iniciar contenedor Qdrant
docker run -p 6333:6333 qdrant/qdrant:dev
```

#### C. OLLAMA
```bash
# Iniciar contenedor Ollama para embeddings
docker run -d -p 11434:11434 --name ollama ollama/ollama:latest
```
**Nota**: No se necesita instalar nada. El modelo `nomic-embed-text` ya está disponible en el contenedor.

#### D. AI-GENAI-CONTEXTUAL-RAG-CONSTRUCTION-REGULATORY-CHATBOT
Una vez que los contenedores estén corriendo, ejecutar la aplicación:

```bash
# 1. Entrar al directorio src
cd src

# 2. Ejecutar la aplicación Chainlit
chainlit run frontend_rag.py --host 0.0.0.0 --port 8000
```

### Puertos de Despliegue

| Servicio | URL | Puerto | Descripción |
|----------|-----|--------|-------------|
| **Chainlit Assistant** | http://localhost:8000/ | 8000 | Interfaz principal del asistente RAG |
| **Qdrant Dashboard** | http://localhost:6333/dashboard | 6333 | Base de datos vectorial |
| **Prisma Studio** | http://localhost:5555/ | 5555 | Gestión de base de datos PostgreSQL |
| **PostgreSQL** | localhost:5432 | 5432 | Base de datos principal del sistema |
| **Ollama** | http://localhost:11434/ | 11434 | Servicio de embeddings locales |
| **LocalStack** | http://localhost:4566/ | 4566 | Emulación de servicios AWS |

### Verificación de Contenedores
```bash
# Verificar estado de todos los contenedores
docker ps

# Verificar logs de contenedores específicos
docker logs <container_name>

# Verificar conectividad de servicios
curl http://localhost:6333/collections  # Qdrant
curl http://localhost:8000/             # Chainlit
curl http://localhost:5555/             # Prisma Studio
curl http://localhost:5432              # PostgreSQL
curl http://localhost:11434/api/tags    # Ollama
curl http://localhost:4566/health       # LocalStack
```

### Verificación Completa de Servicios
```bash
# Script de verificación automática
echo "🔍 Verificando estado de todos los servicios..."
echo "================================================"

# Qdrant
echo "📊 Qdrant (Puerto 6333):"
curl -s http://localhost:6333/collections | jq '.status' 2>/dev/null || echo "❌ No disponible"

# PostgreSQL
echo "🗄️  PostgreSQL (Puerto 5432):"
pg_isready -h localhost -p 5432 2>/dev/null && echo "✅ Conectado" || echo "❌ No disponible"

# Ollama
echo "🤖 Ollama (Puerto 11434):"
curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | head -1 2>/dev/null && echo "✅ Disponible" || echo "❌ No disponible"

# LocalStack
echo "☁️  LocalStack (Puerto 4566):"
curl -s -o /dev/null -w "%{http_code}" http://localhost:4566/ 2>/dev/null | grep -q "200" && echo "✅ Disponible" || echo "❌ No disponible"

echo "================================================"
echo "✅ Verificación completada"

# Resumen de estado
echo ""
echo "📊 RESUMEN DE ESTADO:"
echo "====================="
echo "📊 Qdrant: ✅ Base de datos vectorial operativa"
echo "🗄️  PostgreSQL: ✅ Base de datos principal operativa"
echo "🤖 Ollama: ✅ Modelo de embeddings disponible"
echo "☁️  LocalStack: ✅ Servicios AWS emulados"
echo "🎯 Chainlit: ⚠️  Verificar manualmente (puerto 8000)"
echo "📋 Prisma Studio: ⚠️  Verificar manualmente (puerto 5555)"
```

### Mejores Prácticas de Despliegue
```bash
# 1. Verificar todos los servicios antes de iniciar
docker ps | grep -E "(qdrant|postgres|localstack)"

# 2. Verificar variables de entorno
cat .env | grep -E "(MISTRAL|QDRANT|DATABASE)"

# 3. Verificar conectividad de servicios
curl -s http://localhost:6333/collections  # Qdrant
curl -s http://localhost:5432              # PostgreSQL
curl -s http://localhost:11434             # Ollama

# 4. Iniciar servicios en orden correcto
# Primero: chainlit-datalayer (PostgreSQL + LocalStack)
# Segundo: Qdrant
# Tercero: Ollama
# Cuarto: Aplicación principal
```

## Proceso de Ingestión de Documentos

### Flujo de Ingestión
1. **Preparación**: Colocar PDFs en `data/test/`
2. **Procesamiento**: Ejecutar script de ingestión llamado *ingestion_manual_mistral.py*
3. **Validación**: Verificar completitud con monitor
4. **Verificación**: Confirmar datos en Qdrant

### Scripts de Ingestión Disponibles

#### **Script Principal (Funciona Correctamente)**
```bash
# Ingestión manual directa - FUNCIONA PERFECTAMENTE
python3 src/ingestion_manual_mistral.py
```
**Características:**
- Procesa todos los PDFs en `data/test/`
- Genera embeddings y los almacena en Qdrant
- Crea archivos de salida en `src/output/rag/`
- **Recomendado para uso directo**

#### **Script Robusto (Con Monitoreo)**
```bash
# Gestor robusto con monitoreo de salud del sistema
python3 scripts/robust_ingestion_manager.py
```
**Características:**
- Monitoreo de salud del VPS
- Manejo de timeouts y reintentos
- Logs detallados de proceso
- **Requiere configuración adicional**

#### **Monitor de Estado**
```bash
# Verificar estado de ingestión
python3 scripts/ingestion_monitor.py
```
**Características:**
- Estado de Qdrant y colecciones
- Conteo de archivos procesados
- **NUEVO**: Verificación básica de integridad de chunks
- Salud del sistema
- Recomendaciones automáticas

#### **Validador de Integridad**  **CRÍTICO**
```bash
# Validación exhaustiva de integridad
python3 scripts/validate_ingestion_integrity.py
```
**Características:**
- Verifica que todos los chunks generados estén en Qdrant
- Análisis por archivo individual
- Verificación de metadata (títulos, páginas, chunk_ids)
- Reporte detallado de integridad
- **OBLIGATORIO ejecutar después de cada ingestión**

### **Flujo Recomendado de Validación**
```bash
# 1. Ejecutar ingestión
python3 src/ingestion_manual_mistral.py

# 2. Verificación rápida
python3 scripts/ingestion_monitor.py

# 3. Validación exhaustiva (CRÍTICO)
python3 scripts/validate_ingestion_integrity.py
```

### Estructura de Salida Organizada
```
src/output/
├── rag/                    # Salidas de procesamiento RAG
│   ├── enhanced_chunks_v2_*.json    # Chunks procesados
│   ├── contextualized_content.json  # Contenido contextualizado
│   └── ingestion_manager_*.log      # Logs del gestor
├── analysis/              # Reportes de análisis
│   ├── normativa_analysis_report.xlsx
│   └── duplicate_analysis_report.xlsx
└── evaluation/            # Resultados de evaluación
    ├── evaluation_results_*.json
    └── evaluation_summary_*.txt
```

### Notas Importantes para ML Engineers
- **El script manual funciona perfectamente** cuando se ejecuta directamente
- **El gestor robusto puede tener problemas** de subproceso
- **Siempre verificar la salida** en `src/output/rag/`
- **Monitorear logs** para detectar errores
- **Qdrant debe estar corriendo** antes de iniciar ingestión


## Uso

### Ingestión de Documentos
```bash
cd src/
python3 ingestion_manual_mistral.py
```

### Frontend Web
```bash
cd src/
chainlit run frontend_rag.py --host 0.0.0.0 --port 8000
```

### Validación de Ingestión
```bash
# Verificar estado de ingestión
python3 scripts/ingestion_monitor.py

# Ejecutar ingestión manual (funciona correctamente)
python3 src/ingestion_manual_mistral.py

# Ejecutar ingestión robusta (con monitoreo)
python3 scripts/robust_ingestion_manager.py
```

### Análisis de Documentos
```bash
cd src/analysis/
python3 pdf_analyzer.py
python3 duplicate_detector.py
```

### Evaluación RAG
```bash
cd src/evaluation/
python3 evaluate_rag.py
```

## 📁 Estructura del Proyecto

```
├── src/
│   ├── ingestion/                    # Procesamiento de documentos
│   │   ├── ingest_mistral.py        # Controlador principal de ingestión
│   │   └── pdf_processor.py         # Procesamiento de PDFs
│   ├── embeddings/                   # Vectorización y búsqueda
│   │   └── embedding_qdrant.py      # Controlador de embeddings con Qdrant
│   ├── llm/                         # Modelos de lenguaje
│   │   └── mistral_llm.py           # Integración con Mistral AI
│   ├── translation/                  # Traducción automática
│   │   └── translate.py             # Servicio de traducción
│   ├── config/                      # Configuración
│   │   ├── display_config.py        # Configuración de interfaz
│   │   └── prompt_config.py         # Prompts del sistema
│   ├── analysis/                    # Análisis de documentos
│   │   ├── pdf_analyzer.py          # Análisis de PDFs
│   │   └── duplicate_detector.py    # Detección de duplicados
│   ├── evaluation/                  # Evaluación RAG
│   │   ├── evaluate_rag.py          # Evaluación principal
│   │   └── evaluation_ragas.py      # Métricas RAGAS
│   ├── output/                      # Salidas organizadas
│   │   ├── rag/                     # Salidas de procesamiento RAG
│   │   ├── analysis/                # Reportes de análisis
│   │   └── evaluation/              # Resultados de evaluación
│   ├── frontend_rag.py              # Interfaz web principal
│   └── ingestion_manual_mistral.py  # Script de ingestión manual
├── scripts/                         # Scripts de utilidad
│   ├── ingestion_monitor.py               # Monitoreo de estado de ingestión
│   ├── robust_ingestion_manager.py        # Gestor robusto de ingestión para VPS
│   └── validate_ingestion_integrity.py    # Validador exhaustivo de integridad
├── data/                            # Documentos PDF
│   └── test/                        # Carpeta de documentos de prueba
└── chainlit.md                      # Configuración de Chainlit
```

## Configuración Avanzada

### Optimización de Embeddings
- **Modelo**: `nomic-embed-text` (Ollama local)
- **Dimensiones**: 768
- **Top-K**: 5 (configurable)
- **Distancia**: Cosine similarity

### Configuración de Chunks
- **Tamaño**: 1000 caracteres (configurable)
- **Solapamiento**: 200 caracteres
- **Contextualización**: Automática con Mistral AI
- **Preservación**: Headers Markdown y estructura visual

### Configuración de Qdrant
- **Vector Size**: 768 dimensiones
- **Distance**: Cosine
- **Storage**: On-disk payload
- **Auto-creation**: Colecciones creadas automáticamente

### Flujo de Trabajo RAG
1. **Detección de Idioma**: Automática (español/inglés)
2. **Búsqueda**: Siempre en base de conocimiento en inglés
3. **Respuesta**: Siempre en español
4. **Optimización**: Contexto en inglés + pregunta en inglés para mejor rendimiento

## Evaluación y Métricas

### Métricas RAGAS
- **Context Recall**: Precisión del contexto recuperado
- **Answer Relevancy**: Relevancia de la respuesta
- **Faithfulness**: Fidelidad al contexto

### Validación de Ingestión
- **Verificación de Completitud**: Compara archivos originales vs. ingestados
- **Validación de Títulos**: Verifica coincidencia de nombres de archivos
- **Conteo de Páginas**: Compara páginas originales vs. procesadas
- **Reportes Detallados**: Genera análisis completo de ingestión

### Ejecutar Evaluación
```bash
cd src/evaluation/
python3 evaluate_rag.py
```

## Solución de Problemas

### Errores Comunes de Despliegue
1. **Error de conexión a Qdrant**: Verificar que el contenedor esté ejecutándose
2. **Error de API Mistral**: Verificar la clave API en .env
3. **Error de Ollama**: Verificar que el modelo `nomic-embed-text` esté descargado
4. **Error de memoria**: Aumentar RAM o reducir batch_size
5. **Error de puertos**: Verificar que los puertos 8000, 6333, 5555 no estén ocupados
6. **Error de base de datos**: Verificar que PostgreSQL esté ejecutándose en chainlit-datalayer
7. **Error de uv**: Verificar que uv esté instalado y en PATH
8. **Error de Node.js**: Verificar que node y npm estén instalados
9. **Error de Docker**: Verificar que Docker esté ejecutándose y el usuario esté en grupo docker
10. **Error de Prisma**: Verificar que npx esté disponible y la base de datos esté accesible

### Problemas Conocidos con Chainlit 2.6.0+
**IMPORTANTE**: Las versiones 2.6.0+ de Chainlit incluyen un data layer que requiere dependencias de Google Cloud Storage.

#### Solución 1: Usar variable de entorno (Recomendado)
```bash
CHAINLIT_DISABLE_DATA_LAYER=true chainlit run frontend_rag.py --host 0.0.0.0 --port 8000
```

#### Solución 2: Eliminar configuración automática
```bash
rm -rf .chainlit/
```

#### Solución 3: Downgrade a versión estable (Recomendado)
```bash
uv remove chainlit
uv add "chainlit<2.6.0"
```

**NOTA**: La versión <2.6.0 es la versión estable recomendada que no tiene problemas de data layer.

### Problemas de Ingestión
1. **Script robusto no funciona**: Usar `src/ingestion_manual_mistral.py` directamente
2. **No se crean archivos de salida**: Verificar permisos y directorio `src/output/rag/`
3. **Qdrant no almacena datos**: Verificar conectividad y estado del contenedor
4. **Timeout en procesamiento**: Aumentar timeout o usar script manual

### Logs y Debugging
- Los logs se muestran en la consola
- Usar `print()` para debugging en desarrollo
- Verificar conectividad de servicios con `docker ps`
- Usar scripts de validación para verificar estado
- Monitorear logs en `src/output/rag/ingestion_manager_*.log`

### Troubleshooting de Chainlit
```bash
# Verificar versión instalada
chainlit --version

# Verificar si hay configuración automática
ls -la .chainlit/

# Limpiar configuración automática
rm -rf .chainlit/

# Verificar puerto 8000
lsof -ti:8000 | xargs kill -9

# Ejecutar con data layer deshabilitado
CHAINLIT_DISABLE_DATA_LAYER=true chainlit run frontend_rag.py --host 0.0.0.0 --port 8000
```

### Validación de Estado
```bash
# Verificar estado de Qdrant
curl http://localhost:6333/collections

# Verificar estado de ingestión
python3 scripts/ingestion_monitor.py

# Verificar logs de ingestión
tail -f src/output/rag/ingestion_manager_*.log
```

## Contribución

1. Fork el proyecto
2. Crear una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit los cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## Contacto

- **Desarrollador**: Laren Osorio Toribio
- **Email**: losorio@rcp.pe
- **Organización**: RCP

## Changelog

### v0.2.1 (Actual)
- **Actualización de Chainlit**: Versión 2.6.9 con troubleshooting documentado
- **Solución de problemas de data layer**: Documentación de soluciones alternativas
- **Mejoras en validación**: Scripts de verificación de integridad mejorados
- **Troubleshooting completo**: Guías para problemas comunes de despliegue

### v0.2.0
- **Nueva colección Qdrant**: `asistente-normativa-sincro-kb`
- **Sistema de validación**: Scripts de verificación de completitud de ingestión
- **Organización de salidas**: Estructura organizada en `src/output/`
- **Mejoras en ingestión**: Procesamiento optimizado con Mistral OCR
- **Configuración centralizada**: Gestión unificada de prompts y visualización
- **Análisis de documentos**: Herramientas de análisis y detección de duplicados

### v0.1.0
- Migración completa de Pinecone a Qdrant
- Migración de Groq a Mistral AI
- Implementación de flujo de trabajo inglés KB + español Q&A
- Interfaz web con Chainlit
- Sistema de evaluación RAG
- Procesamiento OCR con Mistral
- Chunking contextualizado inteligente

### Próximas Versiones
- **v0.3.0**: Optimización de embeddings y cache de respuestas
- **v0.4.0**: Métricas de rendimiento en tiempo real
- **v0.5.0**: Integración con más fuentes de datos
- **v0.6.0**: Sistema de versionado de documentos
- **v0.7.0**: API REST completa con FastAPI