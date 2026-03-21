import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

from config import Config
from rag.retriever import retrieve
from rag.generator import generate_answer

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

@bot.command(name="ask")
async def ask(ctx, *, question: str):
    # Retrieve top context chunks
    results = retrieve(question, top_k=Config.TOP_K, return_scores=False)
    if not results:
        await ctx.send("No relevant documents found in the knowledge base.")
        return

    # Generate answer from context
    answer = generate_answer(results, question)
    await ctx.send(answer)

bot.run(TOKEN)