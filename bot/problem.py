import asyncio
import logging

import aiosqlite
from discord.ext import commands
from discord.ext.commands import Context, group

from bot import Bot
from bot.constants import Guild

log = logging.getLogger(__name__)


def is_teacher():
    async def predicate(ctx):
        return ctx.author.id in Guild.teachers

    return commands.check(predicate)


class Problem(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        asyncio.create_task(self.setup_database())

    async def setup_database(self):
        self.bot.db = await aiosqlite.connect("sssss.db")
        await self.bot.db.execute(
            "CREATE TABLE IF NOT EXISTS problems(id INTEGER PRIMARY KEY, description TEXT)"
        )
        await self.bot.db.execute(
            "CREATE TABLE IF NOT EXISTS test_cases(tc_id INTEGER PRIMARY KEY, input TEXT, output TEXT, problem_number INTEGER, FOREIGN KEY(problem_number) REFERENCES problems(id))"
        )
        await self.bot.db.commit()

    @group(name="problem", aliases=("p",), invoke_without_command=True)
    async def problem_group(self, ctx: Context) -> None:
        await ctx.send_help(ctx.command)

    @problem_group.command(aliases=("p",))
    @is_teacher()
    async def post(self, ctx: Context, *, description: str) -> None:
        log.info(f"{ctx.author} used post with {description=}")
        await self.bot.db.execute(
            "INSERT INTO problems(description) VALUES(?)", (description,)
        )
        await self.bot.db.commit()
        await ctx.send(f"{ctx.author.mention} Successfully added problem!")

    @problem_group.command()
    async def dump(self, ctx: Context) -> None:
        async with self.bot.db.execute("SELECT * FROM problems") as cursor:
            problems = await cursor.fetchall()
        async with self.bot.db.execute("SELECT * FROM test_cases") as cursor:
            test_cases = await cursor.fetchall()

        await ctx.send(str(problems) + "\n" + str(test_cases))

    @problem_group.command(aliases=("e",))
    @is_teacher()
    async def edit(
        self, ctx: Context, problem_number: int, *, description: str
    ) -> None:
        cur = await self.bot.db.cursor()
        await cur.execute(
            "UPDATE problems SET description = ?2 WHERE id = ?1",
            (problem_number, description),
        )
        await self.bot.db.commit()

        log.info("{ctx.author} edited description of problem {problem_number}")
        await ctx.send(
            f"{ctx.author.mention} Successfully updated problem {problem_number}"
        )

    @group(name="testcase", aliases=("tc",), invoke_without_command=True)
    async def test_case_group(self, ctx: Context):
        await ctx.send_help(ctx.command)

    @test_case_group.command(name="add", aliases=("a",))
    @is_teacher()
    async def add_test_case(
        self, ctx: Context, problem_number: int, input: str, output: str
    ) -> None:
        """
        Add a test case to a given problem.
        """
        await self.bot.db.execute(
            "INSERT INTO test_cases(input, output, problem_number) VALUES(?1, ?2, ?3)",
            [input, output, problem_number],
        )
        await self.bot.db.commit()

        log.info(f"{ctx.author} added test case to problem {problem_number}")
        await ctx.send(
            f"{ctx.author.mention} Successfully added test case to problem {problem_number}"
        )


async def setup(bot: Bot):
    await bot.add_cog(Problem(bot))
