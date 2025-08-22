import os, sys
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from llm.mistral_llm import MistralLLM
from translation.translate import translate_text
from embeddings.embedding_qdrant import EmbeddingControllerQdrant

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

load_dotenv(project_root / '.env')

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

app = FastAPI()

# Initialize LLM with Spanish language for user interface
llm = MistralLLM(api_key=MISTRAL_API_KEY)
embedding_admin = EmbeddingControllerQdrant()

def detect_language(text: str) -> str:
    """Simple language detection for Spanish vs English."""
    spanish_indicators = ['á', 'é', 'í', 'ó', 'ú', 'ñ', '¿', '¡', 'de', 'la', 'el', 'en', 'y', 'que', 'por', 'con', 'para']
    text_lower = text.lower()
    
    spanish_count = sum(1 for indicator in spanish_indicators if indicator in text_lower)
    return "español" if spanish_count > 2 else "english"

@app.post("/rag")
def rag(data: dict):
    """
    RAG endpoint implementing English KB + Spanish Q&A workflow.
    
    Workflow:
    1. Detect user question language
    2. Translate to English if needed for KB search
    3. Search English KB
    4. Send English context + English question to LLM
    5. LLM responds in Spanish (using configured prompts)
    """
    question = data.get("question")
    if not question:
        return {"error": "Question is required"}
    
    try:
        # 1) Detect language and prepare search query
        detected_language = detect_language(question)
        
        if detected_language == "español":
            # Translate Spanish question to English for KB search
            search_query = translate_text(question, "es", "en")
            print(f"🔄 Spanish question translated to English: '{question[:50]}...' → '{search_query[:50]}...'")
        else:
            # Keep English question for KB search
            search_query = question
            print(f"🌐 English question used directly for KB search")
        
        # 2) Search English KB using search query
        embed_question = embedding_admin.generate_embeddings(search_query)
        context_response = embedding_admin.load_and_query_qdrant(embed_question, top_k=5)
        context_texts = [match.payload['text'] for match in context_response]
        english_context = "\n".join(context_texts)
        
        print(f"📚 English KB context retrieved: {len(context_texts)} chunks")
        
        # 3) Keep English context and use English question for optimal LLM processing
        # The LLM will receive English context + English question but respond in Spanish
        print(f"🔄 Using English context + English question for optimal LLM processing")
        
        # 4) Ensure LLM responds in Spanish
        llm.language = "español"
        
        # 5) Generate Spanish response using English context + English question
        answer = llm.mistral_chat(context=english_context, question=search_query)
        
        print(f"✅ Spanish response generated successfully")
        
        return {
            "answer": answer,
            "relevant_docs": context_texts,
            "workflow_info": {
                "user_language": detected_language,
                "search_language": "english",
                "response_language": "español",
                "llm_input": "english_context + english_question",
                "llm_output": "spanish_response"
            }
        }
        
    except Exception as e:
        print(f"❌ Error in RAG pipeline: {str(e)}")
        return {
            "error": f"RAG processing failed: {str(e)}",
            "workflow_info": {
                "user_language": detected_language if 'detected_language' in locals() else "unknown",
                "search_language": "english",
                "response_language": "español"
            }
        }
    
if __name__ == "__main__":
    uvicorn.run("api_rag:app", host="localhost", port=8001, reload=True)