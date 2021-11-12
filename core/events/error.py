import discord, difflib, traceback
from discord.ext import commands
from core.views import dymview

class OnError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx:commands.Context):
        await ctx.message.add_reaction("❎")

    @commands.Cog.listener()
    async def on_command_error(self, ctx:commands.Context, error):
        await ctx.message.add_reaction("❎")
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        print("".join(traceback.format_exception(type(error), error,  error.__traceback__)))
        errormbed = discord.Embed(
            color=self.bot.color,
            title=F"❌ An Error Occurred: {ctx.command}",
            description=F"```diff\n- {error}\n```",
            timestamp=ctx.message.created_at
        )
        errormbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=errormbed)
    
def setup(bot):
    bot.add_cog(OnError(bot))