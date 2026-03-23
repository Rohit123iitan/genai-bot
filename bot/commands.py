from rag.retriever import retrieve
from rag.generator import generate_answer


# -----------------------------
# Ask Command 
# -----------------------------
async def ask_command(ctx, query: str, history: str):

    if not query.strip():
        return "Please provide a question.\nExample: `!ask What is AI?`", []

    async with ctx.typing():
        try:
            print(f"[RAG] Retrieving chunks for query: {query}")

            # 🔥 Step 1: Retrieve with scores
            results = retrieve(query, top_k=5, return_scores=True)

            if not results:
                return "No relevant information found in documents.", []

            # 🔥 Step 2: Filter strong matches
            filtered = [r for r in results if r.get("score", 0) > 0.6]

            # 🔥 Step 3: Fallback if nothing strong
            if not filtered:
                filtered = results[:2]

            # 🔥 Step 4: Build context + sources
            context_parts = []
            sources = []

            for chunk in filtered:
                content = chunk.get("content", "")
                source = chunk.get("source", "Unknown")

                if content:
                    context_parts.append(content)
                    sources.append(source)

            context = "\n\n".join(context_parts)

            # 🔥 Step 5: Clean context (VERY IMPORTANT)
            context = clean_context(context)

            # 🔍 DEBUG (keep this for now)
            print("\n==== FINAL CONTEXT ====")
            print(context)
            print("=======================\n")

            # 🔥 Step 6: Generate answer
            answer = generate_answer(
                context=context,
                query=query,
                history=history
            )

            sources = list(set(sources))

            return answer, sources

        except Exception as e:
            print("Error in ask_command:", str(e))
            return "⚠️ Something went wrong while processing your request.", []

def clean_context(text):
    import re

    lines = text.split("\n")
    good_lines = []

    for line in lines:
        line = line.strip()

        if len(line) < 30:
            continue

        if sum(c.isalpha() for c in line) / len(line) < 0.6:
            continue

        good_lines.append(line)

    return "\n".join(good_lines)
# -----------------------------
# Text Summarization Command
# -----------------------------
async def summarize_command(content: str):
    """
    Summarize last text or image.
    content = {
        "text": "...",
        "image": "url"
    }
    """

    try:
        print(f"[RAG] Generating summary for content: {content}")
        text = content

        if text:
            from rag.generator import generate_summary
            return generate_summary(text)

        return "Nothing to summarize."

    except Exception as e:
        print(f"[ERROR] summarize_command: {e}")
        return "Failed to generate summary."


# -----------------------------
# Help Command 
# -----------------------------
async def help_command(ctx):
    """
    Show available commands
    """

    help_text = """
        **GenAI Bot Commands**

        `!ask <question>`  
        → Ask questions based on uploaded documents (with memory)

        `!summarize`  
        → Summarize last query 
        
        `!help`  
        → Show this help message
        """

    await ctx.send(help_text.strip())