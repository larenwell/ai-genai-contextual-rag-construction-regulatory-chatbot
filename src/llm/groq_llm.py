from groq import Groq
from config.prompt_config import get_rag_system_prompt, get_rag_user_prompt, format_prompt

class GroqLLM():
    def __init__(self, groq_api_key: str, language: str = "español"):
        self.groq_client = Groq(api_key=groq_api_key)
        self.language = language

    def rag_process_llm(self, context: str, question: str) -> str:
        # Get prompts from centralized configuration
        system_prompt = get_rag_system_prompt(self.language)
        user_prompt_template = get_rag_user_prompt(self.language)
        
        # Format the user prompt with context and question
        user_prompt = format_prompt(user_prompt_template, context=context, question=question)
        
        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )

        return chat_completion.choices[0].message.content
        