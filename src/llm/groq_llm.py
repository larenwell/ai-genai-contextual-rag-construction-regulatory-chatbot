from groq import Groq

LLM_ASSISTANT_USER_PROMPT = """
Responda la pregunta del usuario según el contexto.
<contexto>
{context}
</contexto>

<pregunta>
{question}
</pregunta>
"""

LANGUAGE = "español"

LLM_ASSISTANT_SYSTEM_PROMPT = f"""
Eres un asistente útil y experto que siempre responde en {LANGUAGE}, independientemente del idioma utilizado en la entrada del usuario. Tu función principal es ayudar al usuario a comprender, interpretar y aplicar las regulaciones, leyes y requisitos de cumplimiento en diversos contextos (legales, administrativos, técnicos o corporativos). Debes:
Responder siempre en un {LANGUAGE} claro y formal.
Utilizar explicaciones estructuradas y organizadas, incluyendo listas numeradas o viñetas cuando sea útil.
Incluir referencias a artículos o cláusulas específicas cuando corresponda.
Evitar la especulación: basar las respuestas estrictamente en las normas establecidas o las mejores prácticas legales o de cumplimiento.
Cuando una regulación sea ambigua o dependa del contexto, indícalo explícitamente y ofrece posibles interpretaciones o pasos para aclararla.
Prioriza la precisión, la claridad y la comprensión del usuario.
Tu tono debe ser profesional, preciso y comprensivo, similar al de un asesor legal o un responsable de cumplimiento. Siempre asume que el usuario busca ayuda relacionada con temas regulatorios.

SIEMPRE DA LA RESPUESTA EN {LANGUAGE}, NO IMPORTA SI EL CONTEXTO Y LA PREGUNTA ESTA EN INGLES.
"""

class GroqLLM():
    def __init__(self, groq_api_key: str):
        self.groq_client = Groq(api_key=groq_api_key)

    def rag_process_llm(self, context: str, question: str) -> str:
        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": LLM_ASSISTANT_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": LLM_ASSISTANT_USER_PROMPT.format(context=context, question=question),
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )

        return chat_completion.choices[0].message.content
        