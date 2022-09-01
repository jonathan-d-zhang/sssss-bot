import re
import typing

from discord import Embed
from discord.errors import HTTPException
from discord.ext import commands
from discord.ext.commands import Context
from discord.ext.commands.converter import Converter

from bot import Bot, constants

# Taken from github.com/python-discord/bot-core
FORMATTED_CODE_REGEX = re.compile(
    r"(?P<delim>(?P<block>```)|``?)"  # code delimiter: 1-3 backticks; (?P=block) only matches if it's a block
    r"(?(block)(?:(?P<lang>[a-z]+)\n)?)"  # if we're in a block, match optional language (only letters plus newline)
    r"(?:[ \t]*\n)*"  # any blank (empty or tabs/spaces only) lines before the code
    r"(?P<code>.*?)"  # extract all code inside the markup
    r"\s*"  # any more whitespace before the end of the code markup
    r"(?P=delim)",  # match the exact same delimiter from the start again
    flags=re.DOTALL | re.IGNORECASE,  # "." also matches newlines, case insensitive
)

CODE_TEMPLATE = """\
from io import StringIO
import sys

sys.stdin = StringIO('{input}')
{code}
"""

CHECK_OUTPUT_TEMPLATE = """\
{mention} Your test case results:
{results}
{summary}
"""


def channel_matches():
    async def predicate(ctx: Context):
        return (
            ctx.channel.id in constants.Guild.student_channels
            or ctx.author.id in constants.Guild.teachers
        )

    return commands.check(predicate)


class CodeblockConverter(Converter):
    @classmethod
    async def convert(cls, ctx: Context, code: str) -> str:
        if match := FORMATTED_CODE_REGEX.search(code):
            return match.group("code")
        return ""


class SnekboxResponse(typing.TypedDict):
    stdout: str
    returncode: int


class CodeEval(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def run(self, code) -> SnekboxResponse:
        r = self.bot.http_session.post(
            constants.Snekbox.snekbox_url, json={"input": code}
        )
        return r.json()

    @commands.command()
    @channel_matches()
    async def check(
        self, ctx: Context, problem_number: int, *, code: CodeblockConverter
    ):
        async with self.bot.db.execute(
            "SELECT * FROM test_cases WHERE problem_number = ?", (problem_number,)
        ) as cursor:
            test_cases = await cursor.fetchall()

        results = []
        all_right = True
        for i, test_case in enumerate(test_cases, start=1):
            result = await self.run(CODE_TEMPLATE.format(input=test_case[1], code=code))
            if result["stdout"] != test_case[2]:
                results.append(
                    f"**Test Case {i}**: :x:\nYour output: ```\n{result['stdout']}\n```Expected output: ```\n{test_case[2]}\n```"
                )
                all_right = False
            else:
                results.append(f"**Test Case {i}**: :white_check_mark:\n")

        if all_right:
            summary = "All test cases passed! Good job :pleading_face: :tada:"
        else:
            summary = "Failed some test cases :frowning:. Try again :("

        await ctx.send(
            CHECK_OUTPUT_TEMPLATE.format(
                mention=ctx.author.mention, results="\n".join(results), summary=summary
            )
        )

    @commands.command(name="eval", aliases=("e",))
    async def eval_command(self, ctx: Context, *, code: CodeblockConverter):
        async with ctx.typing():
            result = await self.run(code)
        # truncate output to 10 lines
        output = "\n".join(result["stdout"].split("\n", 11)[:10])
        await ctx.send(
            f"{ctx.author.mention} Your eval finished with exit code {result['returncode']}:\n```\n{output}\n```"
        )


async def setup(bot: Bot):
    await bot.add_cog(CodeEval(bot))
