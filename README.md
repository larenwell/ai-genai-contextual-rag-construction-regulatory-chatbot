# AI Contextual RAG Assistant for Regulatory Compliance

## Project Description

This project implements an intelligent virtual assistant for regulatory compliance in Spanish, designed to help users understand, interpret, and apply regulations, laws, and compliance requirements across various contexts (legal, administrative, technical, or corporate). The system leverages advanced AI technologies including **Contextual Retrieval-Augmented Generation (RAG)**, vector embeddings, and multilingual processing to provide accurate, contextual responses based on regulatory documents.

**Key Innovation**: This implementation uses **contextual retrieval** rather than traditional RAG, where document chunks are enhanced with contextual information using Dolphin-Mistral LLM before embedding generation, significantly improving retrieval accuracy and relevance.

## Scope

The system encompasses the following key areas:

- **PDF Extraction and Chunking**: PDF extraction, text cleaning, and intelligent chunking with metadata preservation
- **Contextual Document Processing**: AI-enhanced contextual generation of each chunk with Dolphin-Mistral for superior retrieval.
- **Multilingual Support**: Spanish user interface with English document processing and automatic translation
- **Contextual Vector Search**: Semantic similarity search using contextually enhanced embeddings in Pinecone Knowledge Database
- **AI-Powered Responses**: Contextual answers using Groq's LLM (Llama 3.3 70B) with regulatory expertise
- **User Interface**: Interactive chat interface built with Chainlit for seamless user experience
- **Evaluation Framework**: RAG performance assessment using RAGAS metrics for quality assurance

## Objectives

### Primary Objectives
1. **Regulatory Compliance Assistance**: Provide accurate, contextual responses to regulatory questions
2. **Contextual Retrieval**: Implement AI-enhanced document chunking for superior search relevance
3. **Multilingual Processing**: Handle Spanish queries while processing English regulatory documents
4. **Source Attribution**: Always provide traceable sources for responses
5. **Professional Communication**: Maintain formal, precise, and professional tone

### Technical Objectives
1. **Contextual RAG Architecture**: Advanced retrieval system using LLM-enhanced chunks
2. **Scalable Architecture**: Modular design for easy maintenance and extension
3. **Performance Optimization**: Efficient document processing and retrieval
4. **Quality Assurance**: Comprehensive evaluation framework for response quality
5. **User Experience**: Intuitive chat interface with clear source citations

## Implementation Guide

### Prerequisites

- Python 3.13 or higher
- Docker and Docker Compose (for local vector database)
- Ollama with Dolphin-Mistral model installed
- API keys for:
  - Pinecone (vector database)
  - Groq (LLM service)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-contextual-rag-asistente-normativa-sincro
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Crear y activar el virtualenv**
    ```bash
    source .venv/bin/activate
    python --version  # debe mostrar 3.12.x
    ```

4. **Install and setup Ollama with Dolphin-Mistral**
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull Dolphin-Mistral model
   ollama pull dolphin-mistral
   ```

5. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX=your_pinecone_index_name
   GROQ_API_KEY=your_groq_api_key
   ```

### Project Structure

```
ai-contextual-rag-asistente-normativa-sincro/
├── src/
│   ├── embeddings/
│   │   └── embedding_funcs.py      # Vector embedding management
│   ├── evaluation/
│   │   └── evaluate_rag.py         # RAG performance evaluation
│   ├── ingestion/
│   │   └── ingest_funcs.py         # Document processing pipeline
│   ├── llm/
│   │   ├── context_llm.py         # Contextual LLM processing (Dolphin-Mistral)
│   │   └── groq_llm.py            # Groq LLM implementation
│   ├── translation/
│   │   └── translate.py            # Text translation utilities
│   └── rag_process.py              # Main RAG processing logic
├── scripts/
│   ├── build_index.py              # Index building orchestration
│   ├── run_app.sh                  # Application startup script
│   └── run_evaluation.sh           # Evaluation execution script
├── docker-compose.yml              # Local service configuration
└── pyproject.toml                  # Project dependencies
```

## Implementation Details

### Core Components

#### 1. Contextual Document Processing (`src/llm/context_llm.py`)
- **Document Title Extraction**: AI-powered title identification from document content
- **Main Idea Generation**: Extracts the core concept and purpose of each document
- **Contextual Chunk Enhancement**: Generates contextual descriptions for each text chunk
- **Model**: Dolphin-Mistral via Ollama for contextual understanding
- **Context Preservation**: Maintains document-level context for improved retrieval

#### 2. Document Ingestion Pipeline (`src/ingestion/ingest_funcs.py`)
- **PDF Text Extraction**: Extracts text from PDF documents with metadata
- **Intelligent Chunking**: Splits text into optimal chunks (1000 chars with 200 char overlap)
- **Contextual Enhancement**: Each chunk is enriched with contextual information
- **Metadata Preservation**: Maintains page numbers, source information, and chunk relationships

#### 3. Contextual Vector Embedding System (`src/embeddings/embedding_funcs.py`)
- **Model**: Uses Nomic Embed Text model via Ollama
- **Contextual Embeddings**: Generates embeddings from contextually enhanced chunks
- **Vector Database**: Pinecone for scalable similarity search
- **Batch Processing**: Efficient upsert operations with configurable batch sizes
- **Query Interface**: Semantic search with configurable top-k results

#### 4. LLM Integration (`src/llm/groq_llm.py`)
- **Model**: Llama 3.3 70B Versatile via Groq API
- **Prompt Engineering**: Specialized system and user prompts for regulatory compliance
- **Temperature Control**: Low temperature (0.1) for consistent, factual responses
- **Spanish Output**: Always responds in Spanish regardless of input language

#### 5. Translation Layer (`src/translation/translate.py`)
- **Bidirectional Translation**: Spanish ↔ English translation
- **Query Processing**: Translates user queries to English for document search
- **Response Localization**: Ensures responses are in Spanish

#### 6. Contextual RAG Processing (`src/rag_process.py`)
- **Contextual Retrieval**: Semantic search using contextually enhanced embeddings
- **Response Generation**: Context-aware answer generation
- **Source Attribution**: Automatic citation of consulted sources
- **Conversation History**: Maintains chat context for follow-up questions

### Key Features

#### Contextual Retrieval (vs Traditional RAG)
- **AI-Enhanced Chunks**: Each document chunk is enriched with contextual information
- **Document-Level Understanding**: Maintains awareness of document structure and purpose
- **Improved Relevance**: Contextual embeddings provide superior search accuracy
- **Semantic Context**: Chunks include their role and relationship within the document

#### Multilingual Processing
- User interface in Spanish
- Document processing in English
- Automatic translation layer
- Consistent Spanish responses

#### Source Attribution
- Automatic citation of consulted documents
- Page number references
- Relevance scoring (optional)
- Structured source display

#### Quality Assurance
- RAGAS evaluation framework
- Context recall metrics
- Answer relevancy assessment
- Faithfulness evaluation

### Configuration

#### Environment Variables
```env
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=your_pinecone_index_name
GROQ_API_KEY=your_groq_api_key
```

#### Model Configuration
- **Contextual LLM**: `dolphin-mistral` (via Ollama)
- **Embedding Model**: `nomic-embed-text` (via Ollama)
- **Response LLM**: `llama-3.3-70b-versatile` (via Groq)
- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Top-k Results**: 5 (configurable)
- **Context Window**: 12,000 characters (for contextual processing)

### Contextual Processing Workflow

#### 1. Document Analysis
```python
# Extract document title and main idea
title = context_llm.identify_title(document_text)
main_idea = context_llm.generate_main_text_idea(document_text)
```

#### 2. Contextual Chunk Enhancement
```python
# For each chunk, generate contextual description
chunk_context = context_llm.generate_chunk_context(main_idea, chunk_text)
enhanced_chunk = f"{chunk_context}\n\n{chunk_text}"
```

#### 3. Embedding Generation
```python
# Generate embeddings from contextually enhanced chunks
embeddings = embedding_admin.generate_embeddings(enhanced_chunk)
```

### Usage

#### Starting the Application
```bash
# Using the provided script
./scripts/run_app.sh

# Or directly with chainlit
chainlit run src/rag_process.py
```

#### Building Document Index
```bash
# Run the complete indexing pipeline
python scripts/build_index.py
```

#### Running Evaluation
```bash
# Execute RAG performance evaluation
python scripts/run_evaluation.sh
```

### API Limits and Considerations

#### Groq API Limits
- Daily query limit: 1000-1500 queries
- Rate limiting considerations
- Cost optimization strategies

#### Ollama Considerations
- Local Dolphin-Mistral model required
- Memory usage for contextual processing
- Processing time for chunk enhancement

#### Pinecone Considerations
- Vector dimension: 768 (nomic-embed-text)
- Index type: Serverless (AWS us-east-1)
- Metric: Cosine similarity
- Batch size: 100 vectors per upsert

### Performance Optimization

#### Contextual Processing
- Efficient chunk enhancement pipeline
- Memory management for large documents
- Parallel processing capabilities

#### Document Processing
- Parallel processing for large documents
- Memory-efficient chunking
- Metadata optimization

#### Vector Search
- Efficient batch operations
- Query optimization
- Index maintenance

#### Response Generation
- Context length optimization
- Prompt efficiency
- Caching strategies

### Security and Compliance

#### Data Privacy
- Local document processing
- Local contextual enhancement (Ollama)
- Secure API key management
- No data retention in external services

#### Regulatory Compliance
- Source traceability
- Audit trail capabilities
- Professional response standards

### Monitoring and Evaluation

#### Performance Metrics
- Response accuracy
- Context relevance
- User satisfaction
- System performance

#### Quality Assessment
- RAGAS evaluation framework
- Automated testing
- Manual review processes

### Future Enhancements

#### Planned Features
- Multi-document support
- Advanced filtering options
- Export capabilities
- Integration APIs

#### Technical Improvements
- Enhanced contextual strategies
- Advanced prompt engineering
- Performance optimization
- Extended evaluation metrics

## Support and Maintenance

### Troubleshooting
- Check API key configuration
- Verify Pinecone index status
- Monitor Groq API usage
- Ensure Ollama is running with Dolphin-Mistral
- Review error logs

### Maintenance Tasks
- Regular index updates
- Performance monitoring
- Security updates
- Dependency management
- Ollama model updates

This implementation provides a robust, scalable solution for regulatory compliance assistance with strong emphasis on accuracy, traceability, and user experience. The **contextual retrieval approach** sets this system apart from traditional RAG implementations by providing superior search relevance through AI-enhanced document understanding. 