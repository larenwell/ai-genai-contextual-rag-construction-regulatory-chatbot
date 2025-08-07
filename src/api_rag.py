import os, sys
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from llm.groq_llm import GroqLLM
from translation.translate import translate_text
from embeddings.embedding_funcs import EmbeddingController

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

load_dotenv(project_root / '.env')

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI()

llm = GroqLLM(groq_api_key=GROQ_API_KEY)
embedding_admin = EmbeddingController(model_name="nomic-embed-text", pinecone_api_key=PINECONE_API_KEY, pinecone_index=PINECONE_INDEX)

@app.post("/rag")
def rag(data: dict):
    question = data.get("question")
    translated_question = translate_text(question, "en", "es")

    embed_question = embedding_admin.generate_embeddings(translated_question)
    context_response = embedding_admin.load_and_query_pinecone(embed_question, top_k=5)
    context_texts = [match['metadata']['text'] for match in context_response['matches']]
    context = "\n".join(context_texts)
    
    answer = llm.rag_process_llm(context=context, question=translated_question)

    return {
        "answer": answer,
        "relevant_docs": context_texts
    }
    
if __name__ == "__main__":
    uvicorn.run("api_rag:app", host="localhost", port=8000, reload=True)