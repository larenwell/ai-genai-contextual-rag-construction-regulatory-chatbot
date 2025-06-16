import ollama

TITLE_INTERPRETER_PROMPT = """
You're gonna receive the first page of a document, from all the text given you'll extract the title of the document.
The title should be concise and descriptive. For example: "Standard for the Installation of Stationary Pumps for Fire Protection", or "Standard for the Installation of Sprinkler Systems"
Return ONLY the title of the document. DO NOT include any other text or explanation. Do NOT explain it like "The title of the document is: " or "Title: "

<document>
{doc_content}
</document>
""" 

DOCUMENT_CONTEXT_PROMPT = """
Analyze the text and extract the main idea
<document>
{doc_content}
</document>
"""

CHUNK_CONTEXT_PROMPT = """
Given the main idea of the document:
<main_idea>
{main_idea}
</main_idea>

Here is the chunk we want to situate within the whole document
<chunk>
{chunk_content}
</chunk>

Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
Answer only in ENGLISH with the succinct context and nothing else.
"""

# LLM_ASSISTANT_USER_PROMPT = """
# Answer the user's question. Based on the context given. 
# <context>
# {context}
# </context>

# <question>
# {question}
# </question>
# """

# LLM_ASSISTANT_SYSTEM_PROMPT = """
# You are a helpful and expert assistant that always replies in Spanish, regardless of the language used in the user's input. Your primary role is to support the user in understanding, interpreting, and applying regulations, laws, and compliance requirements in various contexts (legal, administrative, technical, or corporate). You must:
# Always respond in clear and formal Spanish.
# Use structured and organized explanations, including numbered lists or bullet points when helpful.
# Include references to specific articles or clauses where applicable.
# Avoid speculation—base responses strictly on established norms or best legal/compliance practices.
# When a regulation is ambiguous or context-dependent, note that explicitly and offer possible interpretations or steps to clarify.
# Prioritize accuracy, clarity, and the user's understanding.
# Your tone should be professional, precise, and supportive—similar to that of a legal advisor or compliance officer. Never switch to English, and always assume the user is seeking help related to regulatory topics.
# """


class LLMContext:
    def __init__(self, model_name="dolphin-mistral"):
        self.model_name = model_name

    def truncate_text(self, text, max_size=12000):
        if len(text) > max_size:
            return text[:max_size]
        
        return text

    def generate_main_text_idea(self, text):
        truncated_text = self.truncate_text(text)

        response = ollama.chat(
            model=self.model_name,
            messages=[
                {"role": "user", "content": DOCUMENT_CONTEXT_PROMPT.format(doc_content=truncated_text)},
            ]
        )

        return response['message']['content']

    def identify_title(self, text):
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {"role": "user", "content": TITLE_INTERPRETER_PROMPT.format(doc_content=text)},
            ]
        )

        return response['message']['content']

    def generate_chunk_context(self, main_idea, chunk):
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {"role": "user", "content": CHUNK_CONTEXT_PROMPT.format(main_idea=main_idea, chunk_content=chunk)},
            ]
        )

        return response['message']['content']
    
    # def chat_llm(self, context, message):
    #     response = ollama.chat(
    #         model=self.model_name,
    #         messages=[
    #             {"role":"system","context":LLM_ASSISTANT_SYSTEM_PROMPT},
    #             {"role": "user", "content": LLM_ASSISTANT_USER_PROMPT.format(context=context, question=message)},
    #         ],
    #         options={
    #             "temperature": 0.1
    #         }
    #     )

    #     return response['message']['content']