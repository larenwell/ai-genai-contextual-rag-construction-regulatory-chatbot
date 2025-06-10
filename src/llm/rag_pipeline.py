# src/llm/rag_pipeline.py

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import ollama

QDRANT_HOST     = "localhost"
QDRANT_PORT     = 6333
COLLECTION_NAME = "normativa"
MODEL_NAME      = "intfloat/multilingual-e5-large-instruct"
TOP_K           = 5

class RAG:
    def __init__(self):
        # Conexión a Qdrant
        self.client   = QdrantClient(url=f"http://{QDRANT_HOST}:{QDRANT_PORT}")
        # Modelo de embeddings
        self.embedder = SentenceTransformer(MODEL_NAME)

    def retrieve(self, query: str) -> list[str]:
        """
        1) Embedea la query
        2) Recupera los TOP_K chunks desde Qdrant
        3) Devuelve la lista de textos
        """
        # 1) Embed
        vector = self.embedder.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).tolist()

        # 2) Search en Qdrant
        hits = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            limit=TOP_K
        )

        # 3) Extrae solo el texto de cada payload
        return [hit.payload["text"] for hit in hits]

    def generate(self, user_query: str) -> str:
        """
        1) Recupera contexto relevante
        2) Construye el prompt incluyendo tu instrucción unificada
        3) Llama al LLM (stub) y devuelve la respuesta
        """
        # 1) Recuperar contexto
        contexts = self.retrieve(user_query)

        # 2) Construir prompt
        prompt  = (
            "Basado en la pregunta del usuario y el contexto dado, responde la pregunta:\n\n"
            "=== CONTEXT ===\n"
            + "\n\n---\n\n".join(contexts)
            + f"\n\nUser Query: {user_query}\n"
            "Answer:"
        )

        # 3) Invocar al LLM
        response = call_your_llm(prompt)
        return response

# Stub para tu llamada real al LLM (ollama, HF, etc.)
def call_your_llm(prompt: str) -> str:
    response = ollama.chat(
        model="dolphin-mistral",
        messages=[
            {"role": "assistant", "content": "You are a helpful AI assistant"},
            {"role": "user", "content": prompt}
        ]
    )
    return response['message']['content']

## Revisar el tema de la temperatura.
#bajar temperatura=0.1
#top p = aumentar
#evitar la alunicación, insertar más referencias para que no alucine.