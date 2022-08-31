import discord
import pathlib
import asyncio
import logging
from bot import constants, Bot
import httpx

discord.utils.setup_logging()

log = logging.getLogger(__name__)

intents = discord.Intents.all()


async def main():
    with httpx.Client() as http_session:
        bot = Bot(
            http_session=http_session,
            command_prefix=constants.Bot.prefix,
            intents=intents,
        )
        await bot.setup_database()
        await bot.load_extension("bot.problem")
        await bot.load_extension("bot.code_eval")

        await bot.start(pathlib.Path(constants.Bot.token_file).read_text())


asyncio.run(main())
