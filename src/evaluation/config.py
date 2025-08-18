"""
Evaluation Configuration

This module contains configuration settings for RAG system evaluation.
"""

# API Configuration
API_CONFIG = {
    "endpoint": "http://localhost:8001/rag",
    "timeout": 300,  # seconds
    "max_retries": 3
}

# LLM Configuration for Evaluation
LLM_CONFIG = {
    "model_name": "dolphin-mistral",
    "request_timeout": 300,
    "timeout": 300,
    "keep_alive": 300
}

# Evaluation Metrics Configuration
METRICS_CONFIG = {
    "context_recall": True,
    "faithfulness": True,
    "factual_correctness": True,
    "answer_relevancy": False,  # Can be enabled if needed
    "context_relevancy": False  # Can be enabled if needed
}

# Evaluation Run Configuration
RUN_CONFIG = {
    "max_workers": 1,
    "timeout": 300,
    "batch_size": 10
}

# Output Configuration
OUTPUT_CONFIG = {
    "results_dir": "src/evaluation/results",
    "results_filename": "evaluation_results.json",
    "detailed_results": True,
    "save_raw_data": False
}

# Dataset Configuration
DATASET_CONFIG = {
    "max_samples": 50,
    "shuffle_samples": True,
    "include_metadata": True
}

# Custom Evaluation Questions (can be extended)
CUSTOM_QUESTIONS = [
    {
        "category": "corrosion",
        "question": "What is the primary hazard of internal corrosion in sprinkler systems?",
        "expected_answer": "Internal corrosion can result in partial or full blockage of piping, reducing water flow and impairing fire protection. It can also cause pinhole leaks, leading to system impairment and equipment damage."
    },
    {
        "category": "air_removal",
        "question": "What is recommended for removing trapped air in wet-pipe systems?",
        "expected_answer": "Install FM Approved automatic or manual air-release valves at the system high points and remove air each time the system is drained and refilled."
    },
    {
        "category": "materials",
        "question": "Why should galvanized steel pipe not be used in wet-pipe systems?",
        "expected_answer": "Galvanized steel pipe should not be used because trapped water can cause corrosion, leading to pinhole leaks and potential hydrogen accumulation hazards in certain conditions."
    },
    {
        "category": "nitrogen_usage",
        "question": "What is the purpose of using nitrogen in dry-pipe or wet-pipe sprinkler systems?",
        "expected_answer": "Nitrogen is used to reduce the presence of oxygen, thereby decreasing oxygen-related corrosion reactions in both dry and wet-pipe systems."
    },
    {
        "category": "nitrogen_concentration",
        "question": "What is the typical nitrogen concentration target in a wet-pipe system?",
        "expected_answer": "At least 98% nitrogen concentration is targeted to effectively reduce corrosion rates."
    }
]

# Evaluation Thresholds
THRESHOLDS = {
    "excellent": 0.9,
    "good": 0.8,
    "acceptable": 0.7,
    "poor": 0.6,
    "unacceptable": 0.5
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_to_file": True,
    "log_file": "evaluation.log"
}

def get_evaluation_config():
    """Get the complete evaluation configuration."""
    return {
        "api": API_CONFIG,
        "llm": LLM_CONFIG,
        "metrics": METRICS_CONFIG,
        "run": RUN_CONFIG,
        "output": OUTPUT_CONFIG,
        "dataset": DATASET_CONFIG,
        "custom_questions": CUSTOM_QUESTIONS,
        "thresholds": THRESHOLDS,
        "logging": LOGGING_CONFIG
    }

def get_api_endpoint():
    """Get the API endpoint URL."""
    return API_CONFIG["endpoint"]

def get_llm_model():
    """Get the LLM model name."""
    return LLM_CONFIG["model_name"]

def get_metrics_list():
    """Get list of enabled metrics."""
    enabled_metrics = []
    for metric, enabled in METRICS_CONFIG.items():
        if enabled:
            enabled_metrics.append(metric)
    return enabled_metrics

def get_output_directory():
    """Get the output directory path."""
    return OUTPUT_CONFIG["results_dir"]

def get_custom_questions():
    """Get the custom evaluation questions."""
    return CUSTOM_QUESTIONS

def get_threshold(level: str):
    """Get threshold value for a specific level."""
    return THRESHOLDS.get(level, 0.5) 