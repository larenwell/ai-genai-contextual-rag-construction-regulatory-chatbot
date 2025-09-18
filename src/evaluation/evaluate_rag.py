import os
import sys
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# Permite importar desde src/
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

# Carga variables de entorno
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

# Tu retrieval + generación
from embeddings.embedding_qdrant import EmbeddingControllerQdrant
from llm.mistral_llm import MistralLLM

# RAG evaluation framework
from ragas.evaluator import RagEvaluator
from ragas.metrics import ContextRecall, AnswerRelevancy, Faithfulness

# Parámetros
TOP_K = 5

# Create organized output directory structure
OUTPUT_DIR = Path("src/output/evaluation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Casos de prueba
TEST_DATA: List[Dict] = [
    {
        "query": "¿Qué dice ...",
        "expected_answer": ["El ...."],
        "expected_contexts": ["Principio ..."],
    },
    # añade más…
]

def save_evaluation_results(results: Dict, test_data: List[Dict], output_dir: Path):
    """Save evaluation results to the evaluation output directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save detailed results
    results_file = output_dir / f"evaluation_results_{timestamp}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'evaluation_date': datetime.now().isoformat(),
            'test_data': test_data,
            'results': results,
            'parameters': {
                'top_k': TOP_K,
                'metrics': ['ContextRecall', 'AnswerRelevancy', 'Faithfulness']
            }
        }, f, indent=2, ensure_ascii=False)
    
    # Save summary report
    summary_file = output_dir / f"evaluation_summary_{timestamp}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("RAG Evaluation Summary\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Evaluation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Test Cases: {len(test_data)}\n")
        f.write(f"Top-K: {TOP_K}\n\n")
        
        f.write("Results:\n")
        f.write("-" * 20 + "\n")
        for metric, score in results.items():
            f.write(f"{metric}: {score:.3f}\n")
    
    print(f"📁 Evaluation results saved in: {output_dir}")
    print(f"   📊 Detailed results: {results_file.name}")
    print(f"   📋 Summary report: {summary_file.name}")
    
    return results_file, summary_file

def main():
    # Instancia controladores
    embedding_admin = EmbeddingControllerQdrant()
    llm = MistralLLM(api_key=os.getenv("MISTRAL_API_KEY"))

    # Wrappers para ragas
    def retrieve(query: str) -> List[str]:
        vec = embedding_admin.generate_embeddings(query)
        res = embedding_admin.load_and_query_qdrant(vec, top_k=TOP_K)
        return [m.payload["text"] for m in res]

    def generate(query: str) -> str:
        ctxs = retrieve(query)
        merged = "\n\n---\n\n".join(ctxs)
        return llm.mistral_chat(context=merged, question=query)

    # Creamos el evaluator
    evaluator = RagEvaluator(
        retriever=retrieve,
        generator=generate,
        top_k=TOP_K,
        metrics=[
            ContextRecall(k=TOP_K),
            AnswerRelevancy(),
            Faithfulness(),
        ],
    )

    # Ejecutamos
    print(f"🔍 Evaluando {len(TEST_DATA)} casos…")
    results = evaluator.evaluate(TEST_DATA)

    # Reporte
    print("\n📊 Resultados de evaluación:")
    for metric, score in results.items():
        print(f" • {metric}: {score:.3f}")
    
    # Save results
    save_evaluation_results(results, TEST_DATA, OUTPUT_DIR)

if __name__ == "__main__":
    main()
