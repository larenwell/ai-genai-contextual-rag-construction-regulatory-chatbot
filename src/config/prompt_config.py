"""
Prompt Configuration Module

This module centralizes all prompt templates and configurations for the RAG system.
This follows best practices for prompt management and makes it easier to:
- Modify prompts without changing code
- Maintain consistency across different parts of the system
- Version control prompt changes
- A/B test different prompt versions

WORKFLOW: English KB + Spanish Q&A
- Knowledge Base: Stored in English (optimal for technical content and search)
- User Interface: Always in Spanish (optimal for user experience)
- LLM Responses: Always in Spanish (consistent user interface)
"""

# Language Configuration
LANGUAGE_CONFIG = {
    "default": "english",        # System default (KB language)
    "supported": ["español", "english", "português"],
    "fallback": "english",       # System fallback (KB language)
    "user_interface": "español"  # User-facing language
}

# System Prompts
SYSTEM_PROMPTS = {
    "rag_assistant": {
        "español": """
Eres un asistente útil y experto que siempre responde en español, independientemente del idioma utilizado en la entrada del usuario. 

Tu función principal es ayudar al usuario a comprender, interpretar y aplicar las regulaciones, leyes y requisitos de cumplimiento en diversos contextos (legales, administrativos, técnicos o corporativos).

Debes:
1. Responder siempre en un español claro y formal
2. Utilizar explicaciones estructuradas y organizadas, incluyendo listas numeradas o viñetas cuando sea útil
3. Incluir referencias a artículos o cláusulas específicas cuando corresponda
4. Evitar la especulación: basar las respuestas estrictamente en las normas establecidas o las mejores prácticas legales o de cumplimiento
5. Cuando una regulación sea ambigua o dependa del contexto, indícalo explícitamente y ofrece posibles interpretaciones o pasos para aclararla
6. Priorizar la precisión, la claridad y la comprensión del usuario

Tu tono debe ser profesional, preciso y comprensivo, similar al de un asesor legal o un responsable de cumplimiento. Siempre asume que el usuario busca ayuda relacionada con temas regulatorios.

IMPORTANTE: SIEMPRE DA LA RESPUESTA EN ESPAÑOL, NO IMPORTA SI EL CONTEXTO Y LA PREGUNTA ESTÁN EN INGLÉS.
""",
        "english": """
You are a helpful and expert assistant that always responds in Spanish for the user interface, regardless of the language used in the user's input.

Your main function is to help the user understand, interpret, and apply regulations, laws, and compliance requirements in various contexts (legal, administrative, technical, or corporate).

You must:
1. Always respond in clear and formal Spanish
2. Use structured and organized explanations, including numbered lists or bullet points when useful
3. Include references to specific articles or clauses when appropriate
4. Avoid speculation: base responses strictly on established regulations or legal/compliance best practices
5. When a regulation is ambiguous or context-dependent, indicate this explicitly and offer possible interpretations or steps to clarify it
6. Prioritize accuracy, clarity, and user understanding

Your tone should be professional, precise, and understanding, similar to that of a legal advisor or compliance officer. Always assume the user is seeking help related to regulatory matters.

IMPORTANT: ALWAYS RESPOND IN SPANISH for the user interface, regardless of the system language or context language.
"""
    }
}

# User Prompts
USER_PROMPTS = {
    "rag_query": {
        "español": """
Responda la pregunta del usuario según el contexto proporcionado.

<contexto>
{context}
</contexto>

<pregunta>
{question}
</pregunta>

Por favor, asegúrese de:
1. Basar su respuesta únicamente en el contexto proporcionado
2. Citar las fuentes específicas cuando sea posible
3. Mantener un tono profesional y formal
4. Responder completamente en español
""",
        "english": """
Answer the user's question based on the provided context.

<context>
{context}
</context>

<question>
{question}
</question>

Please ensure to:
1. Base your answer solely on the provided context
2. Cite specific sources when possible
3. Maintain a professional and formal tone
4. Respond completely in Spanish for the user interface
"""
    }
}

def get_system_prompt(prompt_type: str, language: str = None) -> str:
    """
    Get a system prompt by type and language.
    
    Args:
        prompt_type: Type of prompt (e.g., 'rag_assistant')
        language: Language for the prompt (defaults to default language)
    
    Returns:
        Formatted system prompt string
    """
    if not language:
        language = LANGUAGE_CONFIG["default"]
    
    if language not in LANGUAGE_CONFIG["supported"]:
        language = LANGUAGE_CONFIG["fallback"]
    
    if prompt_type in SYSTEM_PROMPTS:
        return SYSTEM_PROMPTS[prompt_type].get(language, SYSTEM_PROMPTS[prompt_type][LANGUAGE_CONFIG["fallback"]])
    
    raise ValueError(f"Unknown prompt type: {prompt_type}")

def get_user_prompt(prompt_type: str, language: str = None) -> str:
    """
    Get a user prompt by type and language.
    
    Args:
        prompt_type: Type of prompt (e.g., 'rag_query')
        language: Language for the prompt (defaults to default language)
    
    Returns:
        Formatted user prompt string
    """
    if not language:
        language = LANGUAGE_CONFIG["default"]
    
    if language not in LANGUAGE_CONFIG["supported"]:
        language = LANGUAGE_CONFIG["fallback"]
    
    if prompt_type in USER_PROMPTS:
        return USER_PROMPTS[prompt_type].get(language, USER_PROMPTS[prompt_type][LANGUAGE_CONFIG["fallback"]])
    
    raise ValueError(f"Unknown prompt type: {prompt_type}")

def format_prompt(template: str, **kwargs) -> str:
    """
    Format a prompt template with the provided variables.
    
    Args:
        template: Prompt template string
        **kwargs: Variables to format in the template
    
    Returns:
        Formatted prompt string
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required variable in prompt template: {e}")

# Convenience functions for common use cases
def get_rag_system_prompt(language: str = None) -> str:
    """Get the RAG system prompt for the specified language."""
    return get_system_prompt("rag_assistant", language)

def get_rag_user_prompt(language: str = None) -> str:
    """Get the RAG user prompt for the specified language."""
    return get_user_prompt("rag_query", language)

def get_user_interface_language() -> str:
    """Get the user interface language (always Spanish for this workflow)."""
    return LANGUAGE_CONFIG["user_interface"]

def get_system_language() -> str:
    """Get the system language (always English for KB storage)."""
    return LANGUAGE_CONFIG["default"]
