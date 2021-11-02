import discord, expr, asyncio
from discord.ext import commands
import core.views.confirm as cum

class Utility(commands.Cog, description="Useful stuff that are open to everyone"):
    def __init__(self, bot):
        self.bot = bot

    # Calculator
    @commands.command(name="calculator", aliases=["calc"], help="Will calculate the given math")
    async def calculator(self, ctx:commands.Context, *, math:str):
        output = expr.evaluate(math)
        calcmbed = discord.Embed(
            color=self.bot.color,
            title="Here is your math:",
            description=F"Input: **{math}**\nOutput: **{output}**",
            timestamp=ctx.message.created_at
        )
        calcmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=calcmbed)

    # Cleanup
    @commands.command(name="cleanup", aliases=["cu"], help="Will delete bot's messagess")
    async def cleanup(self, ctx:commands.Context, *, amount:int):
        cumbed = discord.Embed(
            color=self.bot.color,
            title=F"Cleaned-up {amount} of bot messages",
        )
        cumbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.channel.purge(limit=amount, check=lambda m: m.author.id == self.bot.user.id, bulk=False)
        await ctx.send(embed=cumbed, delete_after=5)

    # Leave
    @commands.command(name="leave", aliases=["lae"], help="Will make the bot leave")
    @commands.has_guild_permissions(administrator=True)
    async def leave(self, ctx:commands.Context):
        laembed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        laembed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = cum.Confirm(ctx)
        view.message = await ctx.send(content="Are you sure you want the bot to leave:", view=view)
        await view.wait()
        if view.value:
            laembed.title = F"{self.bot.user} has successfully left"
            await ctx.send(embed=laembed, delete_after=2.5)
            await ctx.me.guild.leave()

    # Remind
    @commands.command(name="remind", aliases=["rm"], help="Will remind you with the given task and seconds")
    async def remind(self, ctx:commands.Context, seconds:int, *, task:str):
        await ctx.send(F"{ctx.author.mention}, in {seconds} seconds:, I will remind you About: **{task}**", allowed_mentions=discord.AllowedMentions(users=True))
        await asyncio.sleep(seconds)
        view = discord.ui.View()
        button = discord.ui.Button(label="Go to original message", url=ctx.message.jump_url)
        view.add_item(item=button)
        await ctx.send(F"{ctx.author.mention} Reminded you, as you said in {seconds} seconds, it's been **{discord.utils.format_dt(ctx.message.created_at, style='R')}**, About: **{task}**", view=view, allowed_mentions=discord.AllowedMentions(users=True))

    # AFK
    @commands.command(name="afk", help="Will make you AFK")
    async def afk(self, ctx:commands.Context, *, reason:str=None):
        reason = "You didn't provide anything" if not reason else reason
        afk = self.bot.afks.get(ctx.author.id)
        afkmbed  = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        afkmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not afk:
            afk = self.bot.afks[ctx.author.id] = {"time":discord.utils.utcnow(), "reason":reason, "jump_url":ctx.message.jump_url}
            view = discord.ui.View()
            button = discord.ui.Button(label="Go to original message", url=afk["jump_url"])
            view.add_item(item=button)
            afkmbed.title = "Set your AFK"
            afkmbed.description = F"Reason: **{afk['reason']}**"
            await ctx.send(embed=afkmbed)

def setup(bot):
    bot.add_cog(Utility(bot))