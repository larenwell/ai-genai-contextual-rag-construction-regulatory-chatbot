import os
import sys
from pathlib import Path
from typing import List, Dict

# Permite importar desde src/
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

# Carga variables de entorno
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

# Tu retrieval + generación
from embeddings.embedding_funcs import EmbeddingController
from llm.groq_llm import GroqLLM

# RAG evaluation framework
from ragas.evaluator import RagEvaluator
from ragas.metrics import ContextRecall, AnswerRelevancy, Faithfulness

# Parámetros
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX   = os.getenv("PINECONE_INDEX")
GROQ_API_KEY     = os.getenv("GROQ_API_KEY")
TOP_K            = 5

# Casos de prueba
TEST_DATA: List[Dict] = [
    {
        "query": "¿Qué dice ...",
        "expected_answer": ["El ...."],
        "expected_contexts": ["Principio ..."],
    },
    # añade más…
]

def main():
    # Instancia controladores
    embedding_admin = EmbeddingController(
        model_name="nomic-embed-text",
        pinecone_api_key=PINECONE_API_KEY,
        pinecone_index=PINECONE_INDEX
    )
    llm = GroqLLM(groq_api_key=GROQ_API_KEY)

    # Wrappers para ragas
    def retrieve(query: str) -> List[str]:
        vec = embedding_admin.generate_embeddings(query)
        res = embedding_admin.load_and_query_pinecone(vec, top_k=TOP_K)
        return [m["metadata"]["text"] for m in res.matches]

    def generate(query: str) -> str:
        ctxs = retrieve(query)
        merged = "\n\n---\n\n".join(ctxs)
        return llm.rag_process_llm(context=merged, question=query)

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

if __name__ == "__main__":
    main()
