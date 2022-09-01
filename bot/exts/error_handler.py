import logging

from discord import Embed
from discord.ext.commands import Cog, Context, errors

from bot import Bot
from bot.exts.problem import InvalidProblemNumber, InvalidTestCaseNumber

log = logging.getLogger(__name__)


class ErrorHandler(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def make_embed(self, title: str, body: str) -> Embed:
        return Embed(title=title, color=0xFF0000, description=body)

    @Cog.listener()
    async def on_command_error(self, ctx: Context, e: errors.CommandError):
        log.debug(
            "Command {ctx.command} invoked by {ctx.message.author}"
            f"with error {e.__class__.__name__}"
        )
        if isinstance(e, errors.UserInputError):
            if isinstance(e, errors.MissingRequiredArgument):
                embed = self.make_embed("Missing required argument", e.param.name)
            elif isinstance(e, errors.TooManyArguments):
                embed = self.make_embed("Too many arguments", str(e))
            elif isinstance(e, errors.BadArgument):
                embed = self.make_embed("Bad argument", str(e))
            else:
                embed = self.make_embed(
                    "Input error", "Your input is wrong, try again."
                )
        elif isinstance(e, errors.CommandNotFound):
            embed = self.make_embed("Command not found", "Check your spelling")
        elif isinstance(e, InvalidProblemNumber):
            embed = self.make_embed(
                "Invalid problem number",
                "Problem %d doesn't exist, try again." % e.problem_number,
            )
        elif isinstance(e, InvalidTestCaseNumber):
            embed = self.make_embed(
                "Invalid test case number",
                "Test case %d doesn't exist, try again." % e.test_case_number,
            )
        else:
            embed = self.make_embed("Uh oh", "Some error happened, %s" % str(e))

        await ctx.send(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(ErrorHandler(bot))
