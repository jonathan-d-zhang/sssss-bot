import logging

from discord import Embed
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

    @commands.command()
    async def dump(self, ctx: Context) -> None:
        async with self.bot.db.execute("SELECT * FROM problems") as cursor:
            problems = await cursor.fetchall()
        async with self.bot.db.execute("SELECT * FROM test_cases") as cursor:
            test_cases = await cursor.fetchall()

        await ctx.send(str(problems) + "\n" + str(test_cases))

    @commands.command()
    async def post(self, ctx: Context) -> None:

        async with self.bot.db.execute(
            "SELECT description from problems WHERE problems.active = 1"
        ) as cursor:
            problems = await cursor.fetchall()

        print(problems)

    #        embed = Embed(
    #            color=0x36ff90,
    #        )
    #
    #        await ctx.send(embed=embed)

    @group(name="problem", aliases=("p",), invoke_without_command=True)
    async def problem_group(self, ctx: Context) -> None:
        await ctx.send_help(ctx.command)

    @problem_group.command(name="add", aliases=("a",))
    @is_teacher()
    async def add_problem(self, ctx: Context, *, description: str) -> None:
        log.info(f"{ctx.author} used post")
        await self.bot.db.execute(
            "INSERT INTO problems(description, active) VALUES(?, ?)", (description, 1)
        )
        await self.bot.db.commit()
        await ctx.send(f"{ctx.author.mention} Successfully added problem!")

    @problem_group.command(name="edit", aliases=("e",))
    @is_teacher()
    async def edit_problem(
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
        self, ctx: Context, problem_number: int, *, test_cases: str
    ) -> None:
        """
        Add one or more test cases to a given problem.
        The test cases must follow the format "input::output"
        """

        try:
            cases = list(zip(*([iter(test_cases.split())] * 2), strict=True))  # type: ignore
        except ValueError:
            log.debug(
                "%s used test_case add with different number of inputs and outputs"
                % ctx.author
            )
            await ctx.send(
                embed=Embed(
                    title="Oh no",
                    description="Number of inputs and outputs does not match",
                    color=0xFF0000,
                )
            )
        else:
            await self.bot.db.executemany(
                "INSERT INTO test_cases(input, output, problem_number) VALUES(?1, ?2, ?3)",
                [[input, output, problem_number] for input, output in cases],
            )
            await self.bot.db.commit()

            log.info(
                f"{ctx.author} added {len(cases)} test cases to problem {problem_number}"
            )
            await ctx.send(
                f"{ctx.author.mention} Successfully added test case{'s' * bool(len(cases)-1)} to problem {problem_number}"
            )

    @test_case_group.command(name="edit", aliases=("e",))
    @is_teacher()
    async def edit_test_case(
        self, ctx: Context, tc_number: int, input: str, output: str
    ) -> None:
        log.info(f"{ctx.author} edited test case {tc_number}")
        async with self.bot.db.execute(
            "UPDATE test_cases SET input = ?1, output = ?2 WHERE test_cases.tc_id = ?3",
            (input, output, tc_number),
        ):
            await self.bot.db.commit()

    @test_case_group.command(name="delete", aliases=("d",))
    @is_teacher()
    async def delete_test_case(self, ctx: Context, tc_number: int) -> None:
        log.info(f"{ctx.author} deleted test case {tc_number}")

        async with self.bot.db.execute(
            "DELETE FROM test_cases WHERE test_cases.tc_id = ?", (tc_number,)
        ):
            await self.bot.db.commit()


async def setup(bot: Bot):
    await bot.add_cog(Problem(bot))
