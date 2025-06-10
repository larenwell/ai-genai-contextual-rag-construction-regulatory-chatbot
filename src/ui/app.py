# src/ui/app.py
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

import chainlit as cl
from llm.rag_pipeline import RAG

# Instanciamos nuestro pipeline RAG
rag = RAG()

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

    # 2) pipeline RAG
    respuesta = rag.generate(message.content) #message.content: user_query #respuesta: LLM basandose en el user_query y el context obtenido internamente.

    # 3) enviar la respuesta
    await cl.Message(content=respuesta).send()

    # 4) actualizar historial
    history.append({"role": "assistant", "content": respuesta})
    cl.user_session.set("history", history)
