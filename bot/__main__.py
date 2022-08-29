import discord
from discord.ext import commands
import pathlib
from typing import Optional
import sqlite3

intents = discord.Intents(
    message_content=True,
    messages=True,
)

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def post(ctx, description: str, test_cases: Optional[list[tuple[object, object]]]):
    print("used post")


bot.run(pathlib.Path("../token.txt").read_text())
