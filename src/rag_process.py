# src/ui/app.py
import os, sys
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

import chainlit as cl
from llm.context_llm import LLMContext
from embeddings.embedding_funcs import EmbeddingController
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

load_dotenv(project_root / '.env')

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

# Instanciamos nuestro pipeline RAG
rag = LLMContext()
embedding_admin = EmbeddingController(model_name="nomic-embed-text", pinecone_api_key=PINECONE_API_KEY, pinecone_index=PINECONE_INDEX)

@cl.on_chat_start
async def start():
    """
    Se ejecuta una vez al iniciar la conversación.
    """
    # Inicializamos un historial en la sesión de usuario
    cl.user_session.set("history", [])
    # Mensaje de bienvenida
    await cl.Message(
        content="¡Hola! 🤖 Soy tu asistente de normativa. ¿En qué puedo ayudarte?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """
    Se ejecuta cada vez que el usuario envía un mensaje.
    """
    # 1) historial
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    # 2) Extraer contexto del Pinecone
    embed_question = embedding_admin.generate_embeddings(message.content)
    context = embedding_admin.load_and_query_pinecone(embed_question, top_k=5)
    print(f"Context: {context}")

    # 3) pipeline RAG
    respuesta = rag.chat_llm(context=context, message=message.content) 
    #message.content: user_query #respuesta: LLM basandose en el user_query y el context obtenido internamente.

    # 4) enviar la respuesta
    await cl.Message(content=respuesta).send()

    # 5) actualizar historial
    history.append({"role": "assistant", "content": respuesta})
    cl.user_session.set("history", history)
