#!/usr/bin/env python3
"""
RAG Evaluation Runner

This script provides a command-line interface for running RAG system evaluations
with different configurations and options.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from evaluation.evaluation_ragas import RAGEvaluator
from evaluation.config import (
    get_evaluation_config, get_api_endpoint, get_llm_model,
    get_metrics_list, get_output_directory
)


def run_basic_evaluation(api_endpoint: Optional[str] = None, 
                        model_name: Optional[str] = None,
                        max_workers: int = 1) -> bool:
    """
    Run a basic RAG evaluation.
    
    Args:
        api_endpoint: Custom API endpoint (optional)
        model_name: Custom LLM model name (optional)
        max_workers: Maximum number of workers
        
    Returns:
        True if evaluation succeeded, False otherwise
    """
    print("🚀 Starting Basic RAG Evaluation")
    print("=" * 50)
    
    # Use provided values or defaults from config
    endpoint = api_endpoint or get_api_endpoint()
    model = model_name or get_llm_model()
    
    print(f"📡 API Endpoint: {endpoint}")
    print(f"🤖 LLM Model: {model}")
    print(f"⚙️ Max Workers: {max_workers}")
    
    try:
        # Initialize evaluator
        evaluator = RAGEvaluator(
            api_endpoint=endpoint,
            model_name=model,
            timeout=300
        )
        
        # Run evaluation
        result = evaluator.run_evaluation(max_workers=max_workers)
        
        if result:
            # Display results
            evaluator.print_results_summary(result)
            
            # Save results
            evaluator.save_results(result)
            
            print("\n✅ Basic evaluation completed successfully!")
            return True
        else:
            print("\n❌ Basic evaluation failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        return False


def run_custom_evaluation(custom_questions_file: str,
                         api_endpoint: Optional[str] = None,
                         model_name: Optional[str] = None) -> bool:
    """
    Run evaluation with custom questions from a file.
    
    Args:
        custom_questions_file: Path to JSON file with custom questions
        api_endpoint: Custom API endpoint (optional)
        model_name: Custom LLM model name (optional)
        
    Returns:
        True if evaluation succeeded, False otherwise
    """
    print("🚀 Starting Custom RAG Evaluation")
    print("=" * 50)
    
    # Load custom questions
    try:
        import json
        with open(custom_questions_file, 'r', encoding='utf-8') as f:
            custom_questions = json.load(f)
        
        print(f"📋 Loaded {len(custom_questions)} custom questions from: {custom_questions_file}")
        
    except Exception as e:
        print(f"❌ Error loading custom questions: {e}")
        return False
    
    # Use provided values or defaults from config
    endpoint = api_endpoint or get_api_endpoint()
    model = model_name or get_llm_model()
    
    print(f"📡 API Endpoint: {endpoint}")
    print(f"🤖 LLM Model: {model}")
    
    try:
        # Initialize evaluator
        evaluator = RAGEvaluator(
            api_endpoint=endpoint,
            model_name=model,
            timeout=300
        )
        
        # Override the evaluation dataset
        evaluator.get_evaluation_dataset = lambda: custom_questions
        
        # Run evaluation
        result = evaluator.run_evaluation()
        
        if result:
            # Display results
            evaluator.print_results_summary(result)
            
            # Save results with custom filename
            filename = f"custom_evaluation_{Path(custom_questions_file).stem}.json"
            evaluator.save_results(result, filename)
            
            print("\n✅ Custom evaluation completed successfully!")
            return True
        else:
            print("\n❌ Custom evaluation failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        return False


def show_configuration():
    """Display current evaluation configuration."""
    print("⚙️ Current Evaluation Configuration")
    print("=" * 50)
    
    config = get_evaluation_config()
    
    print(f"📡 API Endpoint: {config['api']['endpoint']}")
    print(f"🤖 LLM Model: {config['llm']['model_name']}")
    print(f"⏱️ Timeout: {config['api']['timeout']} seconds")
    print(f"🔧 Max Workers: {config['run']['max_workers']}")
    print(f"📁 Output Directory: {config['output']['results_dir']}")
    
    print(f"\n📊 Enabled Metrics:")
    for metric, enabled in config['metrics'].items():
        status = "✅" if enabled else "❌"
        print(f"   {status} {metric}")
    
    print(f"\n📋 Custom Questions: {len(config['custom_questions'])} questions")
    print(f"🎯 Evaluation Thresholds:")
    for level, threshold in config['thresholds'].items():
        print(f"   {level}: {threshold}")


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="RAG System Evaluation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run basic evaluation
  python run_evaluation.py
  
  # Run with custom API endpoint
  python run_evaluation.py --endpoint http://localhost:8002/rag
  
  # Run with custom LLM model
  python run_evaluation.py --model llama2
  
  # Run with custom questions
  python run_evaluation.py --custom-questions questions.json
  
  # Show configuration
  python run_evaluation.py --show-config
        """
    )
    
    parser.add_argument(
        "--endpoint", 
        help="Custom API endpoint URL"
    )
    
    parser.add_argument(
        "--model", 
        help="Custom LLM model name"
    )
    
    parser.add_argument(
        "--max-workers", 
        type=int, 
        default=1,
        help="Maximum number of workers (default: 1)"
    )
    
    parser.add_argument(
        "--custom-questions", 
        help="Path to JSON file with custom evaluation questions"
    )
    
    parser.add_argument(
        "--show-config", 
        action="store_true",
        help="Show current evaluation configuration"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Show configuration if requested
    if args.show_config:
        show_configuration()
        return
    
    # Set verbose mode
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Run appropriate evaluation
    if args.custom_questions:
        success = run_custom_evaluation(
            custom_questions_file=args.custom_questions,
            api_endpoint=args.endpoint,
            model_name=args.model
        )
    else:
        success = run_basic_evaluation(
            api_endpoint=args.endpoint,
            model_name=args.model,
            max_workers=args.max_workers
        )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 