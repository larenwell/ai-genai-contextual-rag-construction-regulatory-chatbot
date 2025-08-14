# AI Contextual RAG Assistant - Normativa Sincro

## Project Description

This project implements a **Contextual Retrieval-Augmented Generation (RAG)** system designed for regulatory compliance assistance. The system features a **Spanish user interface** with **English knowledge base storage**, providing multilingual support while maintaining optimal search performance.

**Key Innovation**: This implementation uses a **hybrid language approach** where documents are processed and stored in English for optimal search, while user interactions occur entirely in Spanish, with intelligent translation handling throughout the workflow.

## Scope

The system encompasses the following key areas:

- **Multilingual RAG System**: Spanish UI with English knowledge base for optimal search
- **Document Processing**: PDF extraction and analysis using Mistral OCR
- **Intelligent Translation**: Automatic language detection and translation between Spanish and English
- **Vector Search**: Semantic similarity search using Pinecone vector database
- **AI-Powered Responses**: Contextual answers using Groq LLM models
- **Professional UI**: Clean, modern interface built with Chainlit
- **REST API**: FastAPI backend for programmatic access
- **Quality Assurance**: Comprehensive evaluation framework

## Objectives

### Primary Objectives
1. **Multilingual Regulatory Compliance**: Spanish interface with English document processing
2. **Intelligent Language Handling**: Automatic translation for optimized search
3. **Contextual Retrieval**: AI-enhanced document chunking with metadata preservation
4. **Professional Communication**: Maintain formal, precise, and professional tone
5. **Scalable Architecture**: Modular design for easy maintenance and extension

### Technical Objectives
1. **Language Workflow**: Spanish input → English search → Spanish output
2. **Vector Search Optimization**: Efficient semantic search with English embeddings
3. **Metadata Preservation**: Visual elements, tables, and contextual information
4. **Performance Optimization**: Fast response times and efficient processing
5. **Quality Assurance**: Comprehensive evaluation framework

## Implementation Guide

### Prerequisites

- Python 3.12 or higher
- Groq API key for LLM access
- Pinecone API key for vector database
- Mistral AI API key for OCR processing
- Docker (optional, for local services)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-contextual-rag-asistente-normativa-sincro
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or using uv
   uv sync
   ```

3. **Create and activate virtual environment**
   ```bash
   source .venv/bin/activate
   python --version  # should show 3.12.x
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY=your_groq_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX=your_pinecone_index_name
   MISTRAL_API_KEY=your_mistral_api_key
   ```

### Project Structure

```
ai-contextual-rag-asistente-normativa-sincro/
├── src/
│   ├── analysis/
│   │   └── pdf_analyzer.py                 # PDF analysis utilities
│   ├── config/
│   │   ├── display_config.py               # UI display configuration
│   │   └── prompt_config.py                # LLM prompt management
│   ├── embeddings/
│   │   └── embedding_funcs.py              # Vector embedding management
│   ├── evaluation/
│   │   ├── evaluation_ragas.py             # RAG evaluation framework
│   │   ├── run_evaluation.py               # Evaluation execution
│   │   └── sample_questions.json           # Test questions for evaluation
│   ├── ingestion/
│   │   └── ingest_mistral.py               # Mistral OCR document processing
│   ├── llm/
│   │   └── groq_llm.py                     # Groq LLM integration
│   ├── translation/
│   │   └── translate.py                    # Text translation utilities
│   ├── api_rag.py                          # FastAPI REST endpoint
│   ├── frontend_rag.py                     # Chainlit web interface
│   └── ingestion_manual_mistral.py         # Manual ingestion script
├── scripts/
│   ├── setup_pinecone_index.py             # Pinecone configuration
│   └── setup_project_structure.py          # Project initialization
├── tests/                                  # Test files
├── output/                                 # Processing results and reports
├── chainlit.md                             # Chainlit welcome screen and CSS
└── pyproject.toml                          # Project dependencies
```

## Implementation Details

### Core Components

#### 1. Language Workflow System
- **Spanish Input**: User questions in Spanish
- **English Translation**: Automatic translation for KB search optimization
- **English Context**: Retrieved from English knowledge base
- **Spanish Output**: LLM responses in Spanish for user interface

#### 2. Document Processing (`src/ingestion/ingest_mistral.py`)
- **PDF Extraction**: Text, images, tables, and visual elements
- **Content Chunking**: Intelligent document segmentation
- **Metadata Preservation**: Visual elements, page numbers, and context
- **English Storage**: All content stored in English for optimal search

#### 3. Translation Module (`src/translation/translate.py`)
- **Language Detection**: Automatic Spanish/English identification
- **Bidirectional Translation**: Spanish ↔ English conversion
- **Search Optimization**: English queries for English KB
- **Response Localization**: Spanish output for Spanish UI

#### 4. Vector Search System (`src/embeddings/embedding_funcs.py`)
- **Nomic Embeddings**: `nomic-embed-text` model for vector generation
- **Pinecone Integration**: Vector database for similarity search
- **Metadata Indexing**: Visual elements and contextual information
- **Semantic Search**: Context-aware document retrieval

#### 5. LLM Integration (`src/llm/groq_llm.py`)
- **Groq API**: `llama-3.3-70b-versatile` model
- **Prompt Management**: Centralized prompt configuration
- **Language Control**: Ensures Spanish responses
- **Context Processing**: Handles English input, generates Spanish output

#### 6. User Interface (`src/frontend_rag.py`)
- **Chainlit Framework**: Modern chat interface
- **Spanish Localization**: Complete Spanish UI
- **Source Display**: Clean source attribution
- **Responsive Design**: Professional and accessible interface

#### 7. REST API (`src/api_rag.py`)
- **FastAPI Backend**: Programmatic access to RAG system
- **Language Workflow**: Same multilingual logic as frontend
- **Error Handling**: Comprehensive error management
- **Response Formatting**: Structured API responses

### Key Features

#### Multilingual Support
- **Spanish Interface**: Complete user experience in Spanish
- **English Knowledge Base**: Optimal search performance
- **Automatic Translation**: Seamless language handling
- **Consistent Experience**: Same workflow in both languages

#### Document Processing
- **Visual Elements**: Images, tables, and diagrams preserved
- **Metadata Rich**: Page numbers, chunk types, and context
- **Intelligent Chunking**: Context-aware document segmentation
- **Batch Processing**: Efficient handling of multiple documents

#### Search and Retrieval
- **Semantic Search**: Context-aware document retrieval
- **Visual Context**: Visual elements enhance search relevance
- **Source Attribution**: Clear document and page references
- **Relevance Scoring**: Intelligent result ranking

#### User Experience
- **Professional UI**: Clean, modern interface design
- **Responsive Design**: Works on all device sizes
- **Source Display**: Clear attribution and references
- **Error Handling**: Graceful error recovery

### Configuration

#### Environment Variables
```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=your_pinecone_index_name
MISTRAL_API_KEY=your_mistral_api_key
```

#### Model Configuration
- **LLM Model**: `llama-3.3-70b-versatile` (Groq)
- **Embedding Model**: `nomic-embed-text` (768 dimensions)
- **OCR Model**: Mistral OCR for document processing
- **Chunk Size**: Configurable text segmentation
- **Vector Database**: Pinecone for similarity search

### Usage

#### Web Interface
```bash
# Start the Chainlit interface
python -m chainlit run src/frontend_rag.py
```

#### REST API
```bash
# Start the FastAPI server
python src/api_rag.py
```

#### Manual Ingestion
```bash
# Process documents manually
python src/ingestion_manual_mistral.py
```

#### Evaluation
```bash
# Run RAG evaluation
python src/evaluation/run_evaluation.py
```

### Language Workflow

#### 1. User Input
```python
# User asks question in Spanish
user_question = "¿Cuáles son los requisitos de seguridad?"
```

#### 2. Language Detection & Translation
```python
# Detect language and translate to English for search
if detect_language(user_question) == "spanish":
    search_query = translate_text(user_question, "spanish", "english")
```

#### 3. Knowledge Base Search
```python
# Search English KB with English query
context = search_knowledge_base(search_query)
```

#### 4. LLM Processing
```python
# Send English context + English question to LLM
response = llm.rag_process_llm(
    context=english_context,
    question=english_question,
    language="español"  # Ensure Spanish output
)
```

#### 5. Spanish Response
```python
# LLM responds in Spanish for user interface
# Response: "Los requisitos de seguridad incluyen..."
```

### API Endpoints

#### RAG Query Endpoint
```http
POST /rag
Content-Type: application/json

{
  "question": "¿Cuáles son los requisitos de seguridad?",
  "language": "spanish"
}
```

#### Response Format
```json
{
  "response": "Los requisitos de seguridad incluyen...",
  "sources": [
    {"document": "FMDS0200.pdf", "page": 153},
    {"document": "FMDS0201.pdf", "page": 24}
  ],
  "workflow_info": "Spanish input → English search → Spanish output"
}
```

### Services Used

#### **Core AI Services:**
- **Groq API**: LLM inference (`llama-3.3-70b-versatile`)
- **Pinecone**: Vector similarity search and storage
- **Mistral AI**: OCR and document processing
- **Nomic AI**: Text embedding generation

#### **Infrastructure:**
- **Chainlit**: Web chat interface framework
- **FastAPI**: REST API backend

#### **Cost Considerations:**
- **Groq**: Pay-per-token for LLM inference
- **Pinecone**: Pay-per-vector for storage and search
- **Mistral**: Pay-per-API call for OCR processing
- **Nomic**: Pay-per-embedding generation

### Performance Optimization

#### Search Optimization
- **English KB**: Optimal semantic search performance
- **Vector Indexing**: Efficient similarity search
- **Metadata Filtering**: Context-aware result filtering
- **Caching**: Response caching for common queries

#### Processing Efficiency
- **Batch Processing**: Efficient document ingestion
- **Parallel Processing**: Concurrent document analysis
- **Memory Management**: Optimized chunk processing
- **Error Recovery**: Robust error handling

### Security and Compliance

#### Data Privacy
- **API Security**: Secure API key management
- **No Data Retention**: No persistent storage of sensitive content
- **Secure Communication**: Encrypted API communication

#### Regulatory Compliance
- **Source Traceability**: Complete audit trail
- **Visual Evidence**: Visual content preservation
- **Metadata Tracking**: Comprehensive document metadata

### Monitoring and Evaluation

#### Performance Metrics
- **Response Accuracy**: RAG response quality
- **Search Relevance**: Document retrieval accuracy
- **Language Quality**: Translation and response accuracy
- **User Satisfaction**: End-user feedback

#### Quality Assessment
- **RAGAS Evaluation**: Comprehensive RAG assessment
- **Language Validation**: Translation quality verification
- **Response Consistency**: Output consistency across queries

### Future Enhancements

#### Planned Features
- **Advanced Visual Analysis**: Enhanced image and diagram understanding
- **Multi-format Support**: Additional document formats
- **Real-time Processing**: Live document processing
- **Integration APIs**: Third-party system integration

#### Technical Improvements
- **Enhanced Embeddings**: Specialized models for technical content
- **Advanced Search**: Multi-modal search capabilities
- **Performance Optimization**: Faster processing and reduced costs
- **Extended Evaluation**: Comprehensive quality assessment

## Support and Maintenance

### Troubleshooting
- **API Configuration**: Verify API keys and permissions
- **Document Format**: Ensure PDF compatibility
- **Processing Errors**: Check error logs and recovery options
- **Performance Issues**: Monitor resource usage and optimization

### Maintenance Tasks
- **Regular Updates**: Keep dependencies and models current
- **Performance Monitoring**: Track processing efficiency
- **Quality Assurance**: Regular evaluation of output quality
- **Documentation Updates**: Keep implementation guides current

This implementation provides a robust, scalable solution for multilingual regulatory compliance assistance with intelligent language handling and professional user experience. The **hybrid language approach** ensures optimal search performance while maintaining complete Spanish localization for end users. 