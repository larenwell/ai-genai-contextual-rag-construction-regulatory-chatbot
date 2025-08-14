# RAG System Evaluation Package

## Overview

This package provides comprehensive evaluation tools for RAG (Retrieval-Augmented Generation) systems using RAGAS metrics. It includes tools for evaluating context recall, faithfulness, and factual correctness of RAG responses.

## 📁 Package Structure

```
src/evaluation/
├── __init__.py              # Package initialization
├── evaluation_ragas.py      # Main evaluation class
├── config.py                # Configuration settings
├── run_evaluation.py        # Command-line evaluation runner
├── sample_questions.json    # Sample evaluation questions
├── README.md                # This file
└── results/                 # Output directory (created automatically)
    └── evaluation_results.json
```

## 🚀 Quick Start

### 1. Basic Evaluation

Run a basic evaluation with default settings:

```bash
cd src/evaluation
python run_evaluation.py
```

### 2. Show Configuration

View current evaluation settings:

```bash
python run_evaluation.py --show-config
```

### 3. Custom API Endpoint

Run evaluation against a different API:

```bash
python run_evaluation.py --endpoint http://localhost:8002/rag
```

### 4. Custom LLM Model

Use a different LLM for evaluation:

```bash
python run_evaluation.py --model llama2
```

### 5. Custom Questions

Run evaluation with your own questions:

```bash
python run_evaluation.py --custom-questions my_questions.json
```

## 🔧 Configuration

### API Settings

Edit `config.py` to modify:

```python
API_CONFIG = {
    "endpoint": "http://localhost:8001/rag",
    "timeout": 300,  # seconds
    "max_retries": 3
}
```

### LLM Settings

```python
LLM_CONFIG = {
    "model_name": "dolphin-mistral",
    "request_timeout": 300,
    "timeout": 300,
    "keep_alive": 300
}
```

### Evaluation Metrics

```python
METRICS_CONFIG = {
    "context_recall": True,      # Context relevance
    "faithfulness": True,        # Response faithfulness
    "factual_correctness": True, # Factual accuracy
    "answer_relevancy": False,   # Answer relevance (optional)
    "context_relevancy": False   # Context relevance (optional)
}
```

## 📊 Evaluation Metrics

### 1. **Context Recall**
- Measures how well the retrieved context matches the expected answer
- Higher scores indicate better context retrieval

### 2. **Faithfulness**
- Evaluates how faithful the response is to the retrieved context
- Measures if the response stays true to the source material

### 3. **Factual Correctness**
- Assesses the factual accuracy of the generated response
- Compares against reference answers

## 📋 Custom Questions Format

Create a JSON file with your evaluation questions:

```json
[
  {
    "category": "your_category",
    "question": "Your question here?",
    "expected_answer": "Expected answer or reference text"
  }
]
```

### Sample Questions File

Use `sample_questions.json` as a template for your own questions.

## 🎯 Usage Examples

### Python API Usage

```python
from evaluation.evaluation_ragas import RAGEvaluator

# Initialize evaluator
evaluator = RAGEvaluator(
    api_endpoint="http://localhost:8001/rag",
    model_name="dolphin-mistral"
)

# Run evaluation
result = evaluator.run_evaluation()

# Save results
evaluator.save_results(result, "my_results.json")

# Display summary
evaluator.print_results_summary(result)
```

### Command Line Options

```bash
# Basic evaluation
python run_evaluation.py

# Custom endpoint and model
python run_evaluation.py --endpoint http://localhost:8002/rag --model llama2

# Custom questions with verbose output
python run_evaluation.py --custom-questions questions.json --verbose

# Show help
python run_evaluation.py --help
```

## 📈 Understanding Results

### Score Interpretation

- **0.9+**: Excellent performance
- **0.8-0.9**: Good performance
- **0.7-0.8**: Acceptable performance
- **0.6-0.7**: Poor performance
- **<0.6**: Unacceptable performance

### Result Structure

```json
{
  "context_recall": 0.85,
  "faithfulness": 0.78,
  "factual_correctness": 0.82
}
```

## 🔍 Troubleshooting

### Common Issues

1. **API Connection Error**
   - Verify the API endpoint is running
   - Check network connectivity
   - Verify API response format

2. **LLM Model Not Found**
   - Ensure Ollama is running
   - Check model name spelling
   - Pull the model: `ollama pull dolphin-mistral`

3. **Timeout Errors**
   - Increase timeout values in config
   - Check system resources
   - Reduce max_workers

4. **Import Errors**
   - Install required packages: `pip install ragas langchain-ollama`
   - Check Python path configuration

### Debug Mode

Enable verbose logging:

```bash
python run_evaluation.py --verbose
```

## 🚀 Advanced Usage

### Custom Evaluation Datasets

```python
from evaluation.evaluation_ragas import RAGEvaluator

evaluator = RAGEvaluator()

# Override default dataset
evaluator.get_evaluation_dataset = lambda: your_custom_questions

# Run evaluation
result = evaluator.run_evaluation()
```

### Batch Processing

```python
# Process multiple API endpoints
endpoints = [
    "http://localhost:8001/rag",
    "http://localhost:8002/rag",
    "http://localhost:8003/rag"
]

for endpoint in endpoints:
    evaluator = RAGEvaluator(api_endpoint=endpoint)
    result = evaluator.run_evaluation()
    evaluator.save_results(result, f"results_{endpoint.split('/')[-1]}.json")
```

### Custom Metrics

```python
from ragas.metrics import AnswerRelevancy, ContextRelevancy

# Add custom metrics
metrics = [
    LLMContextRecall(),
    Faithfulness(),
    FactualCorrectness(),
    AnswerRelevancy(),      # Additional metric
    ContextRelevancy()      # Additional metric
]

result = evaluate(
    dataset=dataset,
    metrics=metrics,
    llm=evaluator_llm,
    run_config=run_config
)
```

## 📚 Dependencies

### Required Packages

```bash
pip install ragas langchain-ollama requests
```

### Optional Dependencies

```bash
pip install pandas matplotlib seaborn  # For result visualization
pip install jupyter                     # For notebook usage
```

## 🔄 Integration

### With Existing RAG Systems

The evaluator can be integrated with any RAG system that provides:
- POST endpoint accepting `{"question": "..."}`
- JSON response with `{"answer": "...", "relevant_docs": [...]}`

### With CI/CD Pipelines

```yaml
# Example GitHub Actions workflow
- name: Run RAG Evaluation
  run: |
    cd src/evaluation
    python run_evaluation.py --endpoint ${{ secrets.RAG_API_ENDPOINT }}
```

## 📊 Performance Optimization

### Parallel Processing

```python
# Increase workers for faster evaluation
result = evaluator.run_evaluation(max_workers=4)
```

### Batch Size

```python
# Process questions in batches
config = get_evaluation_config()
config['run']['batch_size'] = 20
```

## 🎯 Best Practices

1. **Question Quality**: Ensure evaluation questions are clear and specific
2. **Reference Answers**: Provide accurate, comprehensive reference answers
3. **Regular Evaluation**: Run evaluations regularly to monitor system performance
4. **Result Analysis**: Analyze trends in evaluation scores over time
5. **Continuous Improvement**: Use evaluation results to improve RAG system

## 🤝 Contributing

To contribute to the evaluation package:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This evaluation package is part of the RAG System project.

## 🆘 Support

For questions or issues:

1. Check the troubleshooting section
2. Review the configuration options
3. Test with sample questions
4. Check API connectivity
5. Verify Ollama setup

---

**The evaluation package provides comprehensive tools for assessing RAG system performance. Use it regularly to monitor and improve your system's quality and reliability.** 