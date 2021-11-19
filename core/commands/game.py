import discord, random, typing
from discord.ext import commands

class RPSButtons(discord.ui.Button):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.ctx = view.ctx
        self.botoption = view.botoption
        self.useroption = view.useroption
    async def callback(self, interaction:discord.Interaction):
        if self.label == "Rock":
            self.useroption = "🗻Rock"
        elif self.label == "Paper":
            self.useroption = "🧻Paper"
        elif self.label == "✂️Scissors":
            self.useroption = "✂️Scissors"
        self.view.clear_items()
        if self.useroption == self.botoption:
            tierpsmbed = discord.Embed(
                color=self.ctx.bot.color,
                description=F"We both chose **{self.botoption}**, It's a tie",
                timestamp=interaction.message.created_at
            )
            tierpsmbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=tierpsmbed, view=self.view)
        else:
            if self.useroption == "🗻Rock" and self.botoption == "✂️Scissors" \
               or self.useroption == "🧻Paper" and self.botoption == "🗻Rock" \
                   or self.useroption == "✂️Scissors" and self.botoption == "🧻Paper":
                        wonrpsmbed = discord.Embed(
                            color=self.ctx.bot.color,
                            description=F"You chose **{self.useroption}**, But, I chose **{self.botoption}**, You won / I lost",
                            timestamp=interaction.message.created_at
                        )
                        wonrpsmbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
                        await interaction.response.edit_message(embed=wonrpsmbed, view=self.view)
            elif self.useroption == "✂️Scissors" and self.botoption == "🗻Rock" \
                or self.useroption == "🗻Rock" and self.botoption == "🧻Paper" \
                    or self.useroption == "🧻Paper" and self.botoption == "✂️Scissors":
                        lostrpsmbed = discord.Embed(
                            color=self.ctx.bot.color,
                            description=F"I chose **{self.botoption}**, But, You chose **{self.useroption}**, I won / You lost",
                            timestamp=interaction.message.created_at
                        )
                        lostrpsmbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
                        await interaction.response.edit_message(embed=lostrpsmbed, view=self.view)
class RPSView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.botoption = random.choice(["🗻Rock", "🧻Paper", "✂️Scissors"])
        self.useroption = ""
        self.add_item(item=RPSButtons(emoji="🗻", label="Rock", style=discord.ButtonStyle.green, view=self))
        self.add_item(item=RPSButtons(emoji="🧻", label="Paper", style=discord.ButtonStyle.red, view=self))
        self.add_item(item=RPSButtons(emoji="✂️", label="Scissors", style=discord.ButtonStyle.blurple, view=self))
    async def on_timeout(self):
        if self.children:
            self.clear_items()
            self.add_item(discord.ui.Button(emoji="💣", label="You took so long to answer...", style=discord.ButtonStyle.red, disabled=True))
            await self.message.edit(view=self)
    async def interaction_check(self, interaction:discord.Interaction):
        if interaction.user.id == self.ctx.message.author.id:
            return True
        else:
            icheckmbed = discord.Embed(
                color=self.ctx.bot.color,
                title=F"You can't use this",
                description=F"{interaction.user.mention} - Only {self.ctx.author.mention} can use this\nCause they did the command\nIf you want to use this, do what they did",
                timestamp=interaction.message.created_at
            )
            icheckmbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=icheckmbed, ephemeral=True)
            return False

class CFButtons(discord.ui.Button):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.ctx = view.ctx
        self.botoption = view.botoption
        self.useroption = view.useroption
    async def callback(self, interaction:discord.Interaction):
        if self.label == "Heads":
            self.useroption = "Heads"
        elif self.label == "Tails":
            self.useroption = "Tails"
        self.view.clear_items()
        if self.useroption == self.botoption:
            wonrpsmbed = discord.Embed(
                color=self.ctx.bot.color,
                description=F"It was **{self.useroption}**, You guessed correctly",
                timestamp=interaction.message.created_at
            )
            wonrpsmbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=wonrpsmbed, view=self.view)
        else:
            lostrpsmbed = discord.Embed(
                color=self.ctx.bot.color,
                description=F"It was **{self.botoption}**, You guessed incorrectly **{self.useroption}**",
                timestamp=interaction.message.created_at
            )
            lostrpsmbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=lostrpsmbed, view=self.view)
class CFView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.botoption = random.choice(["Heads", "Tails"])
        self.useroption = ""
        self.add_item(item=CFButtons(emoji="💀", label="Heads", style=discord.ButtonStyle.red, view=self))
        self.add_item(item=CFButtons(emoji="⚡", label="Tails", style=discord.ButtonStyle.green, view=self)) 
    async def on_timeout(self):
        if self.children:
            self.clear_items()
            self.add_item(discord.ui.Button(emoji="💣", label="You took so long to answer...", style=discord.ButtonStyle.red, disabled=True))
            await self.message.edit(view=self)
    async def interaction_check(self, interaction:discord.Interaction):
        if interaction.user.id == self.ctx.message.author.id:
            return True
        else:
            icheckmbed = discord.Embed(
                color=self.ctx.bot.color,
                title=F"You can't use this",
                description=F"{interaction.user.mention} - Only {self.ctx.author.mention} can use this\nCause they did the command\nIf you want to use this, do what they did",
                timestamp=interaction.message.created_at
            )
            icheckmbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=icheckmbed, ephemeral=True)
            return False

class GuessButtons(discord.ui.Button):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.ctx = view.ctx
        self.choose = view.choose
        self.number = view.number
    async def callback(self, interaction:discord.Interaction):
        if self.label == self.number:
            self.choose = True
        elif self.label != self.number:
            self.choose = False
        self.view.clear_items()
        if self.choose == True:
            truembed = discord.Embed(
                color=self.ctx.bot.color,
                title="You guessed correctly",
                description=F"The number was **{self.number}**"
            )
            truembed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=truembed, view=self.view)
        else:
            falsembed = discord.Embed(
                color=self.ctx.bot.color,
                title="You guessed incorrectly",
                description=F"The correct answer was **{self.number}** but you chose **{self.label}**"
            )
            falsembed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=falsembed, view=self.view)

class GuessView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.choose = None
        self.number = random.randint(1, 3)
        for _ in range(1, 4):
            self.add_item(item=GuessButtons(label=_, style=discord.ButtonStyle.green, view=self))
    async def on_timeout(self):
        if self.children:
            self.clear_items()
            self.add_item(discord.ui.Button(emoji="💣", label="You took so long to answer", style=discord.ButtonStyle.red, disabled=True))
            await self.message.edit(view=self)
    async def interaction_check(self, interaction:discord.Interaction):
        if interaction.user.id == self.ctx.message.author.id:
            return True
        else:
            icheckmbed = discord.Embed(
                color=self.ctx.bot.color,
                title=F"You can't use this",
                description=F"{interaction.user.mention} - Only {self.ctx.author.mention} can use this\nCause they did the command\nIf you want to use this, do what they did",
                timestamp=interaction.message.created_at
            )
            icheckmbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=icheckmbed, ephemeral=True)
            return False

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
        view = RPSView(ctx)
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
        view = CFView(ctx)
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
        view = GuessView(ctx)
        view.message = await ctx.reply(embed=gsmbed, view=view)

def setup(bot):
    bot.add_cog(Game(bot))