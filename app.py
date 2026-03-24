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
    print(f"Logged in as {bot.user}")

# -----------------------------
# Register Handlers
# -----------------------------
register_handlers(bot)
register_error_handlers(bot)
# -----------------------------
# Run Bot
# -----------------------------
bot.run(Config.DISCORD_TOKEN)