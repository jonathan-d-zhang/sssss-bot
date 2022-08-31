import re

from discord.ext import commands
from discord.ext.commands.converter import Converter

from bot import constants

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


def channel_matches():
    async def predicate(ctx):
        return (
            str(ctx.channel.id) in constants.Guild.student_channels
            or str(ctx.author.id) in constants.Guild.teachers
        )

    return commands.check(predicate)


class CodeblockConverter(Converter):
    @classmethod
    async def convert(cls, ctx, code: str) -> str:
        if match := FORMATTED_CODE_REGEX.search(code):
            return match.group("code")
        return ""


class CodeEval(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def run(self, code):
        r = self.bot.http_session.post(constants.Snekbox.snekbox_url, data={"input": code})
        return r.json()

    @commands.command()
    @channel_matches()
    async def check(self, ctx, problem_number: int, code: CodeblockConverter):
        ...

    @commands.command(name="eval", aliases=("e",))
    async def eval_command(self, ctx, *, code: CodeblockConverter):
        async with ctx.typing():
            result = await self.run(code)
        await ctx.send(
            f"Your eval output {ctx.author.mention}:\n```\n{result['stdout']}```"
        )


async def setup(bot):
    await bot.add_cog(CodeEval(bot))
