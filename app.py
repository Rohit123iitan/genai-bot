import discord
from discord.ext import commands
import os
from config import Config
from bot.handlers import register_handlers, register_error_handlers


# -----------------------------
# Validate Configuration
# -----------------------------
Config.validate()


# -----------------------------
# Ensure Embeddings Exist (SMART)
# -----------------------------
def ensure_embeddings():
    """
    Run embedder only if DB does not exist.
    """

    if not os.path.exists(Config.DB_PATH):
        print("⚠️ Embeddings DB not found. Running embedder...")

        try:
            from rag.embedder import process_documents
            process_documents()
            print("✅ Embeddings created successfully.")
        except Exception as e:
            print(f"❌ Failed to create embeddings: {e}")
    else:
        print("✅ Embeddings DB found. Skipping embedding step.")


ensure_embeddings()


# -----------------------------
# Bot Setup
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


# -----------------------------
# Events
# -----------------------------
@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")
    print("🚀 Bot is fully operational.")


# -----------------------------
# Register Handlers
# -----------------------------
register_handlers(bot)
register_error_handlers(bot)

print("🔄 Bot process started, waiting for Discord connection...")


# -----------------------------
# Run Bot
# -----------------------------
bot.run(Config.DISCORD_TOKEN)