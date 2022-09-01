import asyncio

import aiosqlite
import httpx
from discord.ext import commands


class Bot(commands.Bot):
    def __init__(self, *args, http_session: httpx.Client, **kwargs):
        super().__init__(*args, **kwargs)
        self.http_session = http_session
        asyncio.create_task(self.setup_database())
        self.db: aiosqlite.Connection

    async def setup_database(self):
        self.db = await aiosqlite.connect("data/sssss.db")
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS problems(id INTEGER PRIMARY KEY, description TEXT, active BOOLEAN)"
        )
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS test_cases(tc_id INTEGER PRIMARY KEY, input TEXT, output TEXT, problem_number INTEGER, FOREIGN KEY(problem_number) REFERENCES problems(id))"
        )
        await self.db.commit()
