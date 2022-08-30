from discord.ext import commands
import logging
import sqlite3

from bot.constants import Guild

log = logging.getLogger(__name__)

def is_teacher():
    async def predicate(ctx):
        return ctx.author.id in Guild.teachers
    return commands.check(predicate)

class Problem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("sssss.db")

        self.setup_database()

    def setup_database(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS problems(id INTEGER PRIMARY KEY, description TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS test_cases(tc_id INTEGER, test_case TEXT, problem_number INTEGER, FOREIGN KEY(problem_number) REFERENCES problems(id)")
        self.conn.commit()

    @commands.command()
    @is_teacher()
    async def post(self, ctx, *, description: str):
        print(f"{ctx.author} used post with {description=}")
        cur = self.conn.cursor()
        cur.execute("INSERT INTO problems(description) VALUES(?)", (description,))
        self.conn.commit()

    @commands.command()
    async def dump(self, ctx):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM problems")
        data = cur.fetchall()
        
        await ctx.send(str(data))
    
    @commands.command()
    @is_teacher()
    async def edit(self, ctx, problem_number: int, *, description: str):
        cur = self.conn.cursor()
        cur.execute("UPDATE problems SET description = ?2 WHERE id = ?1", (problem_number, description))

        log.info("Updated description of %d" % problem_number)
        await ctx.send(f"Successfully updated problem {problem_number}")

async def setup(bot):
    await bot.add_cog(Problem(bot))
