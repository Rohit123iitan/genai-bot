import requests
from config import Config


# -----------------------------
# Build Prompt
# -----------------------------
def build_prompt(context_chunks, query):
    """
    Construct a structured prompt for the LLM.
    """

    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a helpful AI assistant.

Answer the question using ONLY the context below.
If the answer is not in the context, say:
"I couldn't find relevant information in the documents."

Context:
{context}

Question:
{query}

Answer:
"""
    return prompt.strip()


# -----------------------------
# Generate Answer
# -----------------------------
def generate_answer(context_chunks, query):
    """
    Generate answer using retrieved context + LLM.
    """

    if not context_chunks:
        return "No relevant information found."

    prompt = build_prompt(context_chunks, query)

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