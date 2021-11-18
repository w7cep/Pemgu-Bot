import discord
from discord.ext import commands
import core.views.gameview as gv

class Game(commands.Cog, description="Arcade but without having to go outside!"):
    def __init__(self, bot):
        self.bot = bot

    # RockPaperScissors
    @commands.command(name="rockpaperscissors", aliases=["rps"], help="Starts an Rock-Paper-Scissors game")
    async def rockpaperscissors(self, ctx:commands.Context):
        rpsmbed = discord.Embed(
            color=self.bot.color,
            description="Choose your **tool** with the buttons:",
            timestamp=ctx.message.created_at
        )
        rpsmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = gv.RPSView(ctx)
        view.message = await ctx.reply(embed=rpsmbed, view=view)

    # Coinflip
    @commands.command(name="coinflip", aliases=["cf"], help="Starts an Coin-Flip game")
    async def coinflip(self, ctx:commands.Context):
        cfmbed = discord.Embed(
            color=self.bot.color,
            description="**Head** or **Tails**, choose wisely",
            timestamp=ctx.message.created_at
        )
        cfmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = gv.CFView(ctx)
        view.message = await ctx.reply(embed=cfmbed, view=view)

    # Guess
    @commands.command(name="guess", aliases=["gs"], help="Starts an Guessing game")
    async def guess(self, ctx:commands.Context):
        gsmbed = discord.Embed(
            color=self.bot.color,
            description="Try to **guess** now",
            timestamp=ctx.message.created_at
        )
        gsmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = gv.GuessView(ctx)
        view.message = await ctx.reply(embed=gsmbed, view=view)

    # TicTacToe
    @commands.command(name="tictactoe", aliases=["ttt"], help="Starts an Tic-Tac-Toe game")
    @commands.is_owner()
    async def tictactoe(self, ctx:commands.Context):
        await ctx.reply(content="Tic Tac Toe: X goes first", view=gv.TicTacToeView())

def setup(bot):
    bot.add_cog(Game(bot))