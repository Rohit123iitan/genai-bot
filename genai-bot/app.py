import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()  
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not set in environment (.env file missing or variable not defined)")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def help(ctx):
    await ctx.send("Commands:\n!ask <question>\n!help")

bot.run(TOKEN)