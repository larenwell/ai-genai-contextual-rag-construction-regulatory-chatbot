"""
RAG Evaluation using RAGAS

This module provides comprehensive evaluation of RAG systems using RAGAS metrics
including Context Recall, Faithfulness, and Factual Correctness.
"""

import json
import requests
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from ragas import evaluate
from ragas.run_config import RunConfig
from langchain_ollama import OllamaLLM
from ragas.llms import LangchainLLMWrapper
from ragas.dataset_schema import EvaluationDataset
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness


class RAGEvaluator:
    """RAG System Evaluator using RAGAS metrics."""
    
    def __init__(self, api_endpoint: str = "http://localhost:8001/rag", 
                 model_name: str = "dolphin-mistral", timeout: int = 300):
        """
        Initialize the RAG Evaluator.
        
        Args:
            api_endpoint: RAG API endpoint URL
            model_name: Ollama model name for evaluation
            timeout: Request timeout in seconds
        """
        self.api_endpoint = api_endpoint
        self.timeout = timeout
        
        # Initialize Ollama LLM for evaluation
        self.llm = OllamaLLM(
            model=model_name, 
            request_timeout=timeout, 
            timeout=timeout, 
            keep_alive=timeout
        )
        self.evaluator_llm = LangchainLLMWrapper(self.llm)
        
        # Create output directory
        self.output_dir = Path("src/evaluation/results")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def answer_rag(self, question: str) -> Tuple[str, List[str]]:
        """
        Get answer from RAG system.
        
        Args:
            question: User question
            
        Returns:
            Tuple of (answer, relevant_docs)
        """
        try:
            response = requests.post(
                self.api_endpoint, 
                json={"question": question},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            answer = data.get("answer", "")
            relevant_docs = data.get("relevant_docs", [])
            
            return answer, relevant_docs
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error calling RAG API: {e}")
            return "", []
        except KeyError as e:
            print(f"❌ Unexpected response format: {e}")
            return "", []
    
    def get_evaluation_dataset(self) -> List[Dict[str, Any]]:
        """
        Get the evaluation dataset with questions and expected answers.
        
        Returns:
            List of evaluation samples
        """
        return [
            {
                "question": "What is the primary hazard of internal corrosion in sprinkler systems?",
                "answer": "Internal corrosion can result in partial or full blockage of piping, reducing water flow and impairing fire protection. It can also cause pinhole leaks, leading to system impairment and equipment damage."
            },
            {
                "question": "What is recommended for removing trapped air in wet-pipe systems?",
                "answer": "Install FM Approved automatic or manual air-release valves at the system high points and remove air each time the system is drained and refilled."
            },
            {
                "question": "Why should galvanized steel pipe not be used in wet-pipe systems?",
                "answer": "Galvanized steel pipe should not be used because trapped water can cause corrosion, leading to pinhole leaks and potential hydrogen accumulation hazards in certain conditions."
            },
            {
                "question": "What is the purpose of using nitrogen in dry-pipe or wet-pipe sprinkler systems?",
                "answer": "Nitrogen is used to reduce the presence of oxygen, thereby decreasing oxygen-related corrosion reactions in both dry and wet-pipe systems."
            },
            {
                "question": "What is the typical nitrogen concentration target in a wet-pipe system?",
                "answer": "At least 98% nitrogen concentration is targeted to effectively reduce corrosion rates."
            },
            {
                "question": "How does graphitic corrosion affect underground cast iron pipes?",
                "answer": "Graphitic corrosion selectively removes iron from cast iron pipes, leaving behind a weak graphite structure, which can lead to pipe failure, especially in wet soil."
            },
            {
                "question": "What are the signs of microbiologically influenced corrosion (MIC) in sprinkler systems?",
                "answer": "Signs include tubercles or nodule deposits, pinhole leaks, and pitting corrosion, often in stagnant water areas or dead ends of piping."
            },
            {
                "question": "What is the recommended treatment for pipes affected by MIC?",
                "answer": "Chemical treatment is not recommended; instead, replacing the affected pipe is advised."
            },
            {
                "question": "What materials are suggested to avoid corrosion in underground piping?",
                "answer": "FM Approved non-metallic underground pipe is recommended in areas with high water tables or corrosive soil conditions."
            },
            {
                "question": "What is environmental stress cracking (ESC) in CPVC pipes?",
                "answer": "ESC occurs when CPVC pipes absorb organic chemicals under stress, weakening the material and potentially causing cracks or failure."
            }
        ]
    
    def prepare_evaluation_samples(self) -> List[Dict[str, Any]]:
        """
        Prepare evaluation samples by getting responses from RAG system.
        
        Returns:
            List of evaluation samples with responses
        """
        print("🔄 Preparing evaluation samples...")
        
        dataset = self.get_evaluation_dataset()
        sample_dicts = []
        
        for i, sample in enumerate(dataset):
            print(f"   Processing sample {i+1}/{len(dataset)}: {sample['question'][:50]}...")
            
            answer, relevant_docs = self.answer_rag(sample['question'])
            
            sample_dict = {
                "user_input": sample['question'],
                "retrieved_contexts": relevant_docs,
                "response": answer,
                "reference": sample['answer']
            }
            sample_dicts.append(sample_dict)
        
        print(f"✅ Prepared {len(sample_dicts)} evaluation samples")
        return sample_dicts
    
    def run_evaluation(self, max_workers: int = 1) -> Any:
        """
        Run the RAGAS evaluation.
        
        Args:
            max_workers: Maximum number of workers for parallel processing
            
        Returns:
            RAGAS evaluation results
        """
        print("🚀 Starting RAGAS evaluation...")
        
        # Prepare evaluation samples
        sample_dicts = self.prepare_evaluation_samples()
        
        if not sample_dicts:
            print("❌ No evaluation samples prepared")
            return None
        
        # Configure evaluation run
        run_config = RunConfig(timeout=self.timeout, max_workers=max_workers)
        
        # Run evaluation with multiple metrics
        try:
            result = evaluate(
                dataset=EvaluationDataset.from_list(sample_dicts),
                metrics=[
                    LLMContextRecall(), 
                    Faithfulness(), 
                    FactualCorrectness()
                ],
                llm=self.evaluator_llm,
                run_config=run_config
            )
            
            print("✅ Evaluation completed successfully")
            return result
            
        except Exception as e:
            print(f"❌ Error during evaluation: {e}")
            return None
    
    def save_results(self, result: Any, filename: str = "evaluation_results.json") -> None:
        """
        Save evaluation results to file.
        
        Args:
            result: RAGAS evaluation results
            filename: Output filename
        """
        if result is None:
            print("❌ No results to save")
            return
        
        try:
            output_path = self.output_dir / filename
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            
            print(f"💾 Results saved to: {output_path}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    def print_results_summary(self, result: Any) -> None:
        """
        Print a summary of evaluation results.
        
        Args:
            result: RAGAS evaluation results
        """
        if result is None:
            print("❌ No results to display")
            return
        
        print("\n📊 EVALUATION RESULTS SUMMARY")
        print("=" * 50)
        
        try:
            # Convert to dictionary for easier access
            result_dict = result.to_dict()
            
            # Print metrics
            for metric_name, metric_value in result_dict.items():
                if isinstance(metric_value, (int, float)):
                    print(f"{metric_name}: {metric_value:.4f}")
                else:
                    print(f"{metric_name}: {metric_value}")
                    
        except Exception as e:
            print(f"❌ Error displaying results: {e}")
            print("Raw result:", result)


def main():
    """Main function to run RAG evaluation."""
    print("🔍 RAG SYSTEM EVALUATION")
    print("=" * 50)
    
    # Initialize evaluator
    evaluator = RAGEvaluator()
    
    # Run evaluation
    result = evaluator.run_evaluation()
    
    if result:
        # Display results
        evaluator.print_results_summary(result)
        
        # Save results
        evaluator.save_results(result)
        
        print("\n✅ Evaluation completed successfully!")
    else:
        print("\n❌ Evaluation failed")


if __name__ == "__main__":
    main() 