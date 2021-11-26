import discord
from discord.ext import commands
from core.views import confirm, pagination

class Tester(commands.Cog, description="Mad Scientists use these"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pages")
    async def pages(self, ctx:commands.Context):
        t = ["one", "two", "tre"]
        s = []
        for i in t:
            e = discord.Embed(
                color=self.bot.color,
                title=i
            )
            s.append(e)
        await pagination.ViewPagination(ctx, s).start()

def setup(bot):
    bot.add_cog(Tester(bot))