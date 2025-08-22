# src/ui/app.py
import os, sys
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

import chainlit as cl
from llm.mistral_llm import MistralLLM
from translation.translate import translate_text
from embeddings.embedding_qdrant import EmbeddingControllerQdrant
from dotenv import load_dotenv
from config.display_config import (
    get_display_config, get_emoji, get_relevance_icon, 
    get_random_suggestion, format_error_message
)
from config.prompt_config import LANGUAGE_CONFIG

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

load_dotenv(project_root / '.env')


# Load display configuration
DISPLAY_CONFIG = get_display_config()

def format_sources_for_display(context_results):
    if not context_results:  # Just check if the list is empty
        return DISPLAY_CONFIG["error_messages"]["no_sources"]
    
    try:
        # Limit sources based on configuration
        max_sources = DISPLAY_CONFIG["source_display"].get("max_sources_displayed", 5)
        matches = context_results[:max_sources]  # Slice the list directly
        
        # Create a clean sources display with markdown
        sources_text = DISPLAY_CONFIG["source_formatting"].get("header", "### **Fuentes consultadas**\n")
        
        # Add sources as a clean numbered list
        for i, match in enumerate(matches, 1):
            metadata = match.payload
            
            # Extract metadata safely with defaults
            title = metadata.get('book_title', 'Sin título')
            page = metadata.get('page_number', 'N/A')
            header = metadata.get('Header 3') or metadata.get('Header 1', '')
            header_info = f" - {header}" if header else ""
            
            # Calculate score percentage
            score = float(match.score)  # Ensure score is float
            score_percentage = int(score * 100)
            relevance_icon = get_relevance_icon(score_percentage)
            
            # Format source line using template
            source_line = f"{i}. {relevance_icon} **`{title}`** p.{page}{header_info} _(relevancia: {score_percentage}%)_\n"
            sources_text += source_line
        
        return sources_text
        
    except Exception as e:
        print(f"Error formatting sources: {e}")  # Debug log
        return "### **Fuentes consultadas**\n\n*Error al formatear las fuentes. Consulte los logs para más detalles.*"

def format_main_response(response_text):
    """Format the main response with improved spacing and bullet list handling."""
    if not response_text:
        return DISPLAY_CONFIG["error_messages"].get("no_response", "**No se pudo generar una respuesta.**")
    
    try:
        formatted_response = ""
        
        # Add header if configured
        if DISPLAY_CONFIG["response_formatting"].get("add_header", True):
            formatted_response += f"### **Respuesta**\n"
        
        # Add response content with improved spacing
        formatted_response += response_text
        
        # Add footer if configured
        if DISPLAY_CONFIG["response_formatting"].get("add_footer", True):
            footer_text = DISPLAY_CONFIG["response_formatting"].get("footer_text", "*Esta respuesta se generó basándose en la información técnica disponible en los documentos.*")
            formatted_response += f"\n\n{footer_text}"
        
        return formatted_response
        
    except Exception as e:
        print(f"Error formatting response: {e}")
        # Return simple fallback
        return f"### **Respuesta**\n{response_text}"

def create_enhanced_message(content, author="Asistente", elements=None):
    """Create an enhanced message with better visual elements."""
    # Create the main message
    message = cl.Message(
        content=content,
        author=author
    )
    
    # Add elements if provided
    if elements:
        for element in elements:
            message.elements.append(element)
    
    return message

# Initialize LLM with default language defined in the class
llm = MistralLLM(api_key=os.getenv("MISTRAL_API_KEY"))
embedding_admin = EmbeddingControllerQdrant()

def detect_language(text: str) -> str:
    """
    Simple language detection for Spanish vs English.
    This is a basic implementation - you could use a more sophisticated library like 'langdetect'
    """
    # Simple heuristics for language detection
    spanish_indicators = ['á', 'é', 'í', 'ó', 'ú', 'ñ', '¿', '¡', 'de', 'la', 'el', 'en', 'y', 'a', 'es', 'son', 'está', 'tiene']
    english_indicators = ['the', 'and', 'is', 'are', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
    
    text_lower = text.lower()
    spanish_count = sum(1 for indicator in spanish_indicators if indicator in text_lower)
    english_count = sum(1 for indicator in english_indicators if indicator in text_lower)
    
    if spanish_count > english_count:
        return "español"
    elif english_count > spanish_count:
        return "english"
    else:
        return LANGUAGE_CONFIG["default"]

def translate_if_needed(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text if source and target languages are different.
    Optimized for English KB + Spanish Q&A workflow.
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
    
    Returns:
        Translated text or original text if no translation needed
    """
    if source_lang == target_lang:
        return text
    
    try:
        # Map language names to language codes
        lang_code_map = {
            "español": "es",
            "english": "en",
            "português": "pt"
        }
        
        source_code = lang_code_map.get(source_lang, "auto")
        target_code = lang_code_map.get(target_lang, "en")
        
        # Special handling for English KB -> Spanish Q&A
        if source_lang == "english" and target_lang == "español":
            print(f"🔄 Translating English KB content to Spanish for user: '{text[:100]}...'")
        elif source_lang == "español" and target_lang == "english":
            print(f"🔄 Translating Spanish user input to English for KB search: '{text[:100]}...'")
        
        translated = translate_text(text, source_code, target_code)
        print(f"✅ Translation completed: {source_lang} -> {target_lang}")
        return translated
        
    except Exception as e:
        print(f"❌ Translation failed: {e}")
        return text  # Return original text if translation fails

def optimize_for_english_kb_spanish_qa(user_question: str, detected_language: str) -> tuple[str, str, str]:
    """
    Optimize the workflow for English KB + Spanish Q&A.
    
    Args:
        user_question: User's question
        detected_language: Detected language of user question
    
    Returns:
        tuple: (search_query_for_kb, context_language, response_language)
    """
    # Strategy: Always search KB in English, always respond in Spanish
    
    if detected_language == "english":
        # User asked in English, keep for KB search, but respond in Spanish
        search_query = user_question
        context_language = "english"  # KB is in English
        response_language = "español"  # Always respond in Spanish
        print(f"🌐 Strategy: English question -> English KB search -> Spanish response")
        
    else:  # Spanish or other
        # User asked in Spanish, translate to English for KB search, respond in Spanish
        search_query = translate_text(user_question, "es", "en")
        context_language = "english"  # KB is in English
        response_language = "español"  # Always respond in Spanish
        print(f"🌐 Strategy: Spanish question -> English KB search -> Spanish response")
    
    return search_query, context_language, response_language

@cl.on_chat_start
async def start():
    """Initialize the chat session with a welcome message."""
    cl.user_session.set("history", [])
    
    # Show welcome message if configured
    if DISPLAY_CONFIG["visual_elements"].get("welcome_message", True):
        welcome_msg = DISPLAY_CONFIG.get("welcome_message", "## 🚀 **¡Bienvenido al Asistente de Normativa!**\n\n¿En qué puedo ayudarte hoy?")
        await cl.Message(
            content=welcome_msg,
            author="Asistente"
        ).send()

@cl.on_message
async def main(message: cl.Message):
    """Main message handler with improved response formatting."""
    # 1) Update history
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    # 2) Show processing indicator if configured
    if DISPLAY_CONFIG["visual_elements"].get("processing_indicator", True):
        processing_msg = DISPLAY_CONFIG["error_messages"].get("processing", "🔄 **Procesando tu consulta...**")
        await cl.Message(
            content=processing_msg,
            author="Sistema"
        ).send()

    try:
        # 3) Detect language and optimize for English KB + Spanish Q&A workflow
        detected_language = detect_language(message.content)
        
        # 4) Optimize workflow: Always search KB in English, always respond in Spanish
        search_query, context_language, response_language = optimize_for_english_kb_spanish_qa(
            message.content, detected_language
        )
        
        # 5) Extract context from vectorized db using optimized search query
        embed_question = embedding_admin.generate_embeddings(search_query)
        context_response = embedding_admin.load_and_query_qdrant(embed_question, top_k=5)

        print("Context response type:", type(context_response))
        if context_response:
            print("First match payload:", context_response[0].payload if context_response else "No matches")

        context_texts = [match.payload['text'] for match in context_response]
        context = "\n".join(context_texts)

        print(f"Context: {context}")
        print(f"Detected language: {detected_language}")
        print(f"Search query: {search_query}")
        print(f"Context language: {context_language}")
        print(f"Response language: {response_language}")

        # 6) Keep English context and use English question for optimal LLM processing
        # The LLM will receive English context + English question but respond in Spanish
        print(f"🔄 Using English context + English question for optimal LLM processing")
        
        # 7) Set LLM to always respond in Spanish
        llm.language = "español"
        
        # 8) RAG pipeline with English context + English question, Spanish response
        respuesta = llm.mistral_chat(context=context, question=search_query)

        # 7) Create enhanced main response
        formatted_response = format_main_response(respuesta)
        main_message = create_enhanced_message(
            content=formatted_response,
            author="Asistente"
        )
        await main_message.send()
        
        # 6) Display sources with enhanced formatting if configured
        if DISPLAY_CONFIG["visual_elements"].get("source_attribution", True):
            print(f"Number of sources found: {len(context_response) if context_response else 0}")
            
            sources_content = format_sources_for_display(context_response)
            sources_message = create_enhanced_message(
                content=sources_content,
                author="Fuentes"
            )
            await sources_message.send()
        
        # 7) Update history
        history.append({"role": "assistant", "content": respuesta})
        cl.user_session.set("history", history)
        
        # 8) Add helpful follow-up suggestions if configured
        if DISPLAY_CONFIG["visual_elements"].get("follow_up_suggestions", True):
            try:
                suggestion = get_random_suggestion()
                await cl.Message(
                    content=f"**Sugerencia:** {suggestion}",
                    author="Sistema"
                ).send()
            except Exception as e:
                print(f"Error getting suggestion: {e}")
                # Continue without suggestion if there's an error
        
    except Exception as e:
        # Error handling with user-friendly message if configured
        if DISPLAY_CONFIG["visual_elements"].get("error_handling", True):
            error_message = format_error_message("processing_error", error=str(e))
            
            await cl.Message(
                content=error_message,
                author="Sistema"
            ).send()
        
        # Log error for debugging
        print(f"Error in main handler: {str(e)}")
        import traceback
        traceback.print_exc()
    