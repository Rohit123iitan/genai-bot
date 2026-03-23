from bot.commands import ask_command, help_command, summarize_command
from collections import defaultdict, deque


# -----------------------------
# User Memory 
# -----------------------------
user_memory = defaultdict(lambda: deque(maxlen=3))


def get_user_history(user_id: int) -> str:
    """
    Convert stored user history into prompt-friendly format.
    """
    history = user_memory[user_id]

    if not history:
        return ""

    formatted = ""
    for item in history:
        formatted += f"Q: {item['question']}\nA: {item['answer']}\n"

    return formatted.strip()


def store_interaction(user_id: int, question: str, answer: str):
    """
    Save a new Q&A interaction for the user.
    """
    user_memory[user_id].append({
        "question": question,
        "answer": answer
    })


# -----------------------------
# Query Cache
# -----------------------------
query_cache = {}

def normalize_query(query: str):
    return " ".join(query.lower().strip().split())

def get_cached(query: str):
    return query_cache.get(normalize_query(query))

def set_cache(query: str, data: dict):
    query_cache[normalize_query(query)] = data


# -----------------------------
# Store Last Content 
# -----------------------------



# -----------------------------
# Register Bot Commands
# -----------------------------
def register_handlers(bot):
    """
    Register all command handlers to the bot.
    """

    # -----------------------------
    # ASK COMMAND (UPDATED)
    # -----------------------------
    @bot.command()
    async def ask(ctx, *, query: str = ""):
        user_id = ctx.author.id
        print(f"[ASK] User {user_id} asked: {query}")
        if not query.strip():
            await ctx.send("Please provide a question.")
            return
        

        cached = get_cached(query)
        print(f"[CACHE] Checking cache for query: {query}") 
        if cached:
            answer = cached["answer"]
            sources = cached.get("sources", [])

            response = answer

            if sources:
                response += "\n\n📚 Sources:\n"
                for s in sources:
                    response += f"- {s}\n"

            await ctx.send(response)
            return

        history_text = get_user_history(user_id)

        answer, sources = await ask_command(ctx, query, history_text)

        if answer:
            store_interaction(user_id, query, answer)

        set_cache(query, {
            "answer": answer,
            "sources": sources
        })

        response = answer

        if sources:
            response += "\n\n📚 Sources:\n"
            for s in sources:
                response += f"- {s}\n"

        await ctx.send(response)

    @bot.command(name="summarize")
    async def summarize(ctx):
        user_id = ctx.author.id

        content = get_user_history(user_id)

        if not content:
            await ctx.send("Nothing to summarize yet.")
            return

        summary = await summarize_command(content)

        await ctx.send(f"Summary:\n{summary}")

    # -----------------------------
    # HELP COMMAND
    # -----------------------------
    @bot.command()
    async def help(ctx):
        await help_command(ctx)

# -----------------------------
# Global Error Handler
# -----------------------------
def register_error_handlers(bot):
    """
    Handle unexpected errors globally.
    """

    @bot.event
    async def on_command_error(ctx, error):
        print(f"[ERROR] {error}")

        await ctx.send(
            "Something went wrong. Please try again."
        )