# Enhanced Mistral OCR Contextual RAG Assistant

## Project Description

This project implements an advanced **Contextual Retrieval-Augmented Generation (RAG)** system that leverages **Mistral OCR** to process both text and visual content from regulatory documents. The system goes beyond traditional RAG by incorporating AI-enhanced document understanding, visual element analysis, and intelligent annotations to provide superior search relevance and contextual responses.

**Key Innovation**: This implementation uses **Mistral OCR** for multimodal document processing, combining text extraction with visual understanding (diagrams, charts, tables, formulas) and contextual enhancement using AI to create superior embeddings for regulatory compliance assistance.

## Scope

The system encompasses the following key areas:

- **Multimodal Document Processing**: PDF extraction with Mistral OCR for text, images, tables, and diagrams
- **Visual Element Understanding**: AI-powered analysis of charts, formulas, and technical diagrams
- **Contextual Document Processing**: AI-enhanced contextual understanding using Mistral models
- **Intelligent Annotation System**: Automatic detection and tagging of requirements, warnings, and important notes
- **Batch Processing**: Efficient processing of multiple documents with progress tracking
- **Multilingual Support**: Spanish user interface with English document processing
- **Contextual Vector Search**: Semantic similarity search using contextually enhanced embeddings
- **AI-Powered Responses**: Contextual answers using advanced LLM models
- **Quality Assurance**: Comprehensive evaluation framework with visual content assessment

## Objectives

### Primary Objectives
1. **Multimodal Regulatory Compliance**: Process text and visual content for comprehensive regulatory assistance
2. **Visual Understanding**: Extract and understand diagrams, charts, tables, and formulas
3. **Contextual Retrieval**: Implement AI-enhanced document chunking with visual context
4. **Intelligent Annotations**: Automatically detect and highlight regulatory requirements and important information
5. **Batch Processing**: Efficient processing of large document collections
6. **Professional Communication**: Maintain formal, precise, and professional tone

### Technical Objectives
1. **Mistral OCR Integration**: Seamless integration with Mistral's OCR capabilities
2. **Visual Context Preservation**: Maintain visual context in document chunks
3. **Scalable Architecture**: Modular design for easy maintenance and extension
4. **Performance Optimization**: Efficient multimodal document processing
5. **Quality Assurance**: Comprehensive evaluation framework for multimodal content

## Implementation Guide

### Prerequisites

- Python 3.12 or higher
- Mistral AI API key with OCR access
- Vector database (Pinecone, Qdrant, or similar)
- Docker and Docker Compose (for local services)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rag-asistente-normativa
   ```

2. **Install dependencies**
   ```bash
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
   MISTRAL_API_KEY=your_mistral_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX=your_pinecone_index_name
   ```

### Project Structure

```
rag-asistente-normativa/
├── src/
│   ├── ingestion/
│   │   ├── ingest_mistral.py              # Original Mistral OCR implementation
│   │   ├── enhanced_mistral_ocr.py        # Enhanced OCR with visual understanding
│   │   └── batch_processor.py             # Batch processing utilities
│   ├── embeddings/
│   │   └── embedding_funcs.py             # Vector embedding management
│   ├── llm/
│   │   ├── context_llm.py                 # Contextual LLM processing
│   │   └── groq_llm.py                    # Response generation
│   ├── translation/
│   │   └── translate.py                   # Text translation utilities
│   └── rag_process.py                     # Main RAG processing logic
├── scripts/
│   ├── run_batch_processing.py            # Batch processing script
│   └── run_evaluation.sh                  # Evaluation execution script
├── output/                                # Processing results and reports
├── docker-compose.yml                     # Local service configuration
└── pyproject.toml                         # Project dependencies
```

## Implementation Details

### Core Components

#### 1. Enhanced Mistral OCR Processing (`src/ingestion/enhanced_mistral_ocr.py`)
- **Multimodal Extraction**: Text, images, tables, diagrams, and formulas
- **Visual Element Detection**: AI-powered identification of visual content
- **Contextual Enhancement**: AI-enhanced chunks with visual context
- **Annotation System**: Automatic detection of requirements, warnings, and important notes
- **Batch Processing**: Efficient handling of multiple documents

#### 2. Visual Element Understanding
- **Image Analysis**: Captioning and description of diagrams and charts
- **Table Processing**: Structure preservation and content extraction
- **Formula Recognition**: Mathematical expression understanding
- **Diagram Interpretation**: Technical diagram analysis and description

#### 3. Intelligent Annotation System
- **Requirement Detection**: Automatic identification of regulatory requirements
- **Warning Recognition**: Detection of safety warnings and cautions
- **Importance Scoring**: Priority-based annotation system
- **Expert Notes**: Contextual annotations for enhanced understanding

#### 4. Batch Processing (`src/ingestion/batch_processor.py`)
- **Concurrent Processing**: Controlled parallel document processing
- **Progress Tracking**: Real-time processing status and metrics
- **Error Handling**: Robust error recovery and reporting
- **Result Management**: Organized output with detailed reports

#### 5. Contextual Vector Embedding System
- **Multimodal Embeddings**: Text and visual content representation
- **Context Preservation**: Visual context in embedding generation
- **Annotation Integration**: Annotation-aware search capabilities
- **Scalable Storage**: Efficient vector database management

### Key Features

#### Multimodal Processing
- **Text + Visual**: Combined processing of text and visual content
- **Context Preservation**: Visual context maintained in chunks
- **Enhanced Search**: Visual elements improve search relevance
- **Comprehensive Understanding**: Full document comprehension

#### Intelligent Annotations
- **Automatic Detection**: AI-powered annotation identification
- **Priority System**: Critical, high, medium, low priority levels
- **Expert Integration**: Support for manual expert annotations
- **Search Enhancement**: Annotations improve retrieval accuracy

#### Batch Processing
- **Scalable**: Process hundreds of documents efficiently
- **Concurrent**: Parallel processing with controlled concurrency
- **Monitoring**: Real-time progress tracking and reporting
- **Error Recovery**: Robust error handling and recovery

#### Visual Understanding
- **Diagram Analysis**: Technical diagram interpretation
- **Chart Recognition**: Data visualization understanding
- **Table Processing**: Structured data extraction
- **Formula Interpretation**: Mathematical expression analysis

### Configuration

#### Environment Variables
```env
MISTRAL_API_KEY=your_mistral_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=your_pinecone_index_name
```

#### Model Configuration
- **OCR Model**: `mistral-ocr-latest`
- **Contextual LLM**: `mistral-large-latest`
- **Embedding Model**: `nomic-embed-text` (768 dimensions)
- **Chunk Size**: 1200 characters
- **Chunk Overlap**: 300 characters
- **Max Concurrent**: 3 documents (configurable)

### Usage

#### Single Document Processing
```python
from src.ingestion.enhanced_mistral_ocr import EnhancedMistralOCRController

controller = EnhancedMistralOCRController(api_key="your_mistral_api_key")
enhanced_chunks = await controller.process_single_document(
    pdf_path="document.pdf",
    book_title="Technical Guide"
)
```

#### Batch Processing
```python
from src.ingestion.batch_processor import BatchProcessor

processor = BatchProcessor(api_key="your_mistral_api_key")
results = await processor.process_documents_batch(
    pdf_paths=["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    book_titles=["Guide 1", "Guide 2", "Guide 3"],
    max_concurrent=2
)
```

#### Running Batch Processing Script
```bash
python scripts/run_batch_processing.py
```

### Visual Processing Workflow

#### 1. Document Analysis
```python
# Extract content with visual elements
extraction_result = await controller.extract_content_mistral_ocr_async(pdf_path)
```

#### 2. Visual Element Detection
```python
# Identify and analyze visual elements
visual_elements = controller.extract_visual_elements_enhanced(chunk_content)
```

#### 3. Contextual Enhancement
```python
# Enhance chunks with visual context
enhanced_chunk = await controller.contextualize_chunk_enhanced(
    chunk, document_summary, book_title, page_num, visual_elements
)
```

#### 4. Annotation Extraction
```python
# Extract intelligent annotations
annotations = controller.extract_annotations(chunk_content, chunk_id)
```

### API Limits and Considerations

#### Mistral OCR Limits
- **Document Size**: Maximum 50MB per document
- **Processing Time**: Varies by document complexity
- **Concurrent Requests**: Rate limiting considerations
- **Cost Optimization**: Efficient batch processing strategies

#### Batch Processing Considerations
- **Memory Usage**: Large document collections require adequate RAM
- **Processing Time**: Visual content increases processing time
- **Error Recovery**: Robust error handling for large batches
- **Storage Requirements**: Enhanced chunks require more storage

### Performance Optimization

#### Visual Processing
- **Parallel Analysis**: Concurrent visual element processing
- **Memory Management**: Efficient handling of large images
- **Caching Strategies**: Cache visual analysis results

#### Batch Processing
- **Concurrency Control**: Optimal parallel processing levels
- **Resource Management**: Efficient memory and CPU usage
- **Progress Monitoring**: Real-time status updates

#### Vector Search
- **Multimodal Indexing**: Efficient visual content indexing
- **Query Optimization**: Enhanced search with visual context
- **Result Ranking**: Improved relevance with visual elements

### Security and Compliance

#### Data Privacy
- **Local Processing**: Sensitive document processing options
- **Secure API**: Encrypted API communication
- **No Data Retention**: No persistent storage of sensitive content

#### Regulatory Compliance
- **Source Traceability**: Complete audit trail
- **Visual Evidence**: Visual content preservation
- **Annotation Tracking**: Annotation history and sources

### Monitoring and Evaluation

#### Performance Metrics
- **Processing Accuracy**: Text and visual extraction quality
- **Visual Understanding**: Diagram and chart interpretation accuracy
- **Annotation Quality**: Requirement and warning detection accuracy
- **Search Relevance**: Enhanced retrieval performance

#### Quality Assessment
- **Multimodal Evaluation**: Text and visual content assessment
- **Annotation Validation**: Expert review of automatic annotations
- **User Satisfaction**: End-user feedback on responses

### Future Enhancements

#### Planned Features
- **Advanced Visual Analysis**: Deep learning for complex diagrams
- **Interactive Annotations**: User-editable annotation system
- **Real-time Processing**: Live document processing capabilities
- **Integration APIs**: Third-party system integration

#### Technical Improvements
- **Enhanced Visual Models**: Specialized models for technical content
- **Advanced Annotation Types**: Domain-specific annotation categories
- **Performance Optimization**: Faster processing and reduced costs
- **Extended Evaluation**: Comprehensive multimodal assessment

## Support and Maintenance

### Troubleshooting
- **API Configuration**: Verify Mistral API key and permissions
- **Document Format**: Ensure PDF compatibility
- **Processing Errors**: Check error logs and recovery options
- **Performance Issues**: Monitor resource usage and optimization

### Maintenance Tasks
- **Regular Updates**: Keep dependencies and models current
- **Performance Monitoring**: Track processing efficiency
- **Quality Assurance**: Regular evaluation of output quality
- **Documentation Updates**: Keep implementation guides current

This enhanced implementation provides a robust, scalable solution for multimodal regulatory compliance assistance with superior visual understanding and intelligent annotation capabilities. The **Mistral OCR integration** sets this system apart by providing comprehensive document understanding that goes beyond traditional text-only RAG systems. 