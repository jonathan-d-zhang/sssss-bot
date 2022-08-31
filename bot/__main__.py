import discord
from discord.ext import commands
import pathlib
import asyncio
import logging
from bot import constants

discord.utils.setup_logging()

log = logging.getLogger(__name__)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    log.info("Ready")


async def main():
    await bot.load_extension("bot.problem")

    await bot.start(pathlib.Path(constants.Bot.token_file).read_text())


asyncio.run(main())
