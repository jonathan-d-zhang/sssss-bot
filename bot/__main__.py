import asyncio
import logging
import pathlib

import discord
import httpx

from bot import Bot, constants

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
        await bot.load_extension("bot.exts.problem")
        await bot.load_extension("bot.exts.code_eval")
        await bot.load_extension("bot.exts.error_handler")

        await bot.start(pathlib.Path(constants.Bot.token_file).read_text())

    await bot.start(pathlib.Path(constants.Bot.token_file).read_text())


asyncio.run(main())
