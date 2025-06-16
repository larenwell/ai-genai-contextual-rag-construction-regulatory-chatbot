# src/ui/app.py
import os, sys
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

import chainlit as cl
from llm.groq_llm import GroqLLM
from translation.translate import translate_text
from embeddings.embedding_funcs import EmbeddingController
from dotenv import load_dotenv


project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

load_dotenv(project_root / '.env')

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def format_sources_for_display(context_results):
    if not context_results or 'matches' not in context_results:
        return "No se encontraron fuentes relevantes."
    
    matches = context_results['matches']
    if not matches:
        return "No se encontraron fuentes relevantes."
    
    sources_text = "## 🤓 Fuentes consultadas:\n\n"
    
    for i, match in enumerate(matches, 1):
        metadata = match.get('metadata', {})
        score = match.get('score', 0)
        
        title = metadata.get('title', 'Sin título')
        page = int(metadata.get('page_number', 0)) if metadata.get('page_number') else 'N/A'
        
        sources_text += f"**Fuente {i}:**\n"
        sources_text += f"- **Documento:** {title}\n"
        sources_text += f"- **Página:** {page}\n"
        sources_text += f"- **Relevancia:** {(score * 100):.2f}%\n\n"
    
    return sources_text

llm = GroqLLM(groq_api_key=GROQ_API_KEY)
embedding_admin = EmbeddingController(model_name="nomic-embed-text", pinecone_api_key=PINECONE_API_KEY, pinecone_index=PINECONE_INDEX)

@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])
    await cl.Message(
        content="¡Hola! 🤖 Soy tu asistente de normativa. ¿En qué puedo ayudarte?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    # 1) historial
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    # 2) Traducir la pregunta al inglés
    message.content = translate_text(message.content)

    # 3) Extraer contexto del Pinecone
    embed_question = embedding_admin.generate_embeddings(message.content)
    context = embedding_admin.load_and_query_pinecone(embed_question, top_k=5)
    print(f"Context: {context}")

    # 4) pipeline RAG
    respuesta = llm.rag_process_llm(context=context, question=message.content)

    # 5) Crear el mensaje principal con la respuesta
    main_message = cl.Message(content=respuesta)
    await main_message.send()
    
    # 5.5) incluir fuentes
    if context:
        sources_content = format_sources_for_display(context)
        await cl.Message(
            content=sources_content,
            author="📚 Fuentes"
        ).send()
    
    # 6) actualizar historial
    history.append({"role": "assistant", "content": respuesta})
    cl.user_session.set("history", history)
    