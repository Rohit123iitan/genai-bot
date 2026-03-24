import requests
from config import Config

# ----------------------------------------------------------------------------------------------
# Build Prompt -> Create a structured prompt for the LLM based on context, query, and history.
# ----------------------------------------------------------------------------------------------
def build_prompt(context_chunks, query, history=""):
    return f"""You are a direct and highly knowledgeable expert assistant. 

Your task is to answer the user's question by synthesizing the provided context_chunks.

Follow these core guidelines:
1. Maximize the context_chunks: Extract and piece together the most useful information from the context_chunks, even if it appears messy, fragmented, or incomplete. 
2. Stay Focused: Be concise and directly address the user's query.
3. Use History for Flow: Only use the chat history to understand pronouns or conversational references. Base your factual answers entirely on the context.
4. DO NOT use introductory filler words.
<context>
{context_chunks}
</context>

<chat_history>
{history}
</chat_history>

<question>
{query}
</question>

Expert Answer:
"""

# ------------------------------------------------------------------------------
# Generate Answer -> Send the prompt to the LLM and return the generated answer.
# -------------------------------------------------------------------------------
def generate_answer(context, query, history=""):
    if not context:
        return "No relevant information found."

    prompt = build_prompt(context, query, history)
    
    try:
        response = requests.post(
            Config.OLLAMA_URL,
            json={
                "model": Config.LLM_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        if response.status_code != 200:
            return f"LLM Error: {response.status_code}"

        data = response.json()
        return data.get("response", "No response from model.")

    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"

# -----------------------------------------------------------------------------
# Generate Summary -> Create a concise summary of the given text using the LLM.
# ------------------------------------------------------------------------------
def generate_summary(text: str):
    if not text.strip():
        return "Nothing to summarize."

    prompt = f"""Summarize the text below.

Use only the provided text.
Do not say you cannot access data.
Keep it concise.

Text:
{text}

Summary:
"""
    try:
        response = requests.post(
            Config.OLLAMA_URL,
            json={
                "model": Config.LLM_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        if response.status_code != 200:
            return f"LLM Error: {response.status_code}"

        data = response.json()
        return data.get("response", "No summary generated.")

    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"