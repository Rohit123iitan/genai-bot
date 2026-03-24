from bot.commands import ask_command, help_command, summarize_command
from collections import defaultdict, deque

user_memory = defaultdict(lambda: deque(maxlen=3))

# ---------------------------------------------------------------------------------------------
# Memory Management -> Handle user-specific memory with a simple in-memory structure.
# ---------------------------------------------------------------------------------------------


def store_interaction(user_id: int, question: str, answer: str):
    user_memory[user_id].append({
        "question": question,
        "answer": answer
    })


def get_user_history(user_id: int) -> str:

    history = user_memory[user_id]

    if not history:
        return ""

    formatted = ""
    for item in history:
        formatted += f"Q: {item['question']}\nA: {item['answer']}\n"

    return formatted.strip()


# -------------------------------------------------------------------------------------------------
# Query Cache -> Implement a simple in-memory cache to store recent queries and their responses.
# -------------------------------------------------------------------------------------------------
query_cache = {}


def normalize_query(query: str):
    return " ".join(query.lower().strip().split())


def get_cached(query: str):
    return query_cache.get(normalize_query(query))


def set_cache(query: str, data: dict):
    query_cache[normalize_query(query)] = data

# -----------------------------------------------------------------------------
# Register Bot Commands -> Define all command handlers for the bot.
# -----------------------------------------------------------------------------
def register_handlers(bot):
    @bot.command()
    async def ask(ctx, *, query: str = ""):
        user_id = ctx.author.id
        if not query.strip():
            await ctx.send("Please provide a question.")
            return

        cached = get_cached(query)

        if cached:
            answer = cached["answer"]
            sources = cached.get("sources", [])

            response = answer

            if sources:
                response += "\n\n Sources:\n"
                for s in sources:
                    response += f"- {s}\n"

            await ctx.send(response)
            return

        history_text = get_user_history(user_id)

        answer, sources = await ask_command(ctx, query, history_text)

        if answer and "error" not in answer.lower():
            store_interaction(user_id, query, answer)

        set_cache(query, {
            "answer": answer,
            "sources": sources
        })

        response = answer

        if sources:
            response += "\n\n Sources:\n"
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

    @bot.command()
    async def help(ctx):
        await help_command(ctx)

# ---------------------------------------------------------------------------------------------
# Global Error Handler -> Catch unhandled exceptions and provide feedback to the user.
# ---------------------------------------------------------------------------------------------
def register_error_handlers(bot):
    @bot.event
    async def on_command_error(ctx, error):
        print(f"[ERROR] {error}")

        await ctx.send(
            "Something went wrong. Please try again."
        )
