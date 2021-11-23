import discord, os, random, typing, io
from discord.ext import commands

class CounterView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.clicks = 0
        self.clickers = ""
    @discord.ui.button(emoji="👏", style=discord.ButtonStyle.green)
    async def click(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.edit_message(view=button.view)
        self.clicks += 1
        if str(interaction.user) in self.clickers:
            pass
        else: self.clickers += F"{str(interaction.user)}\n"
    async def on_timeout(self):
        for item in self.children:
            self.clear_items()
        ontimeoutmbed = discord.Embed(
            color=self.ctx.bot.color,
            title=F"Button was clicked: {self.clicks} times",
        )
        if len(self.clickers) != 0 or self.clicks != 0:
            ontimeoutmbed.description = "People who clicked:\n"
            ontimeoutmbed.description += self.clickers
        else: ontimeoutmbed.description = "Nobody clicked the buttons"
        await self.message.edit(embed=ontimeoutmbed, view=self)

class NitroView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
    @discord.ui.button(label="ACCEPT", style=discord.ButtonStyle.green)
    async def accept(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.send_message(content="https://imgur.com/NQinKJB", ephemeral=True)
    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if not item.disabled:
                    item.label = "EXPIRED"
                    item.style = discord.ButtonStyle.red
                    item.disabled = True
                    ontimeoutmbed = discord.Embed(
                        color=self.ctx.bot.color,
                        title="THE NITRO HAS EXPIRED",
                        description="The gift link has either expired or has been revoked.",
                        timestamp=self.ctx.message.created_at
                    )
                    ontimeoutmbed.set_footer(text=self.ctx.author, icon_url=self.ctx.author.display_avatar.url)
                    await self.message.edit(embed=ontimeoutmbed, view=self)

class Fun(commands.Cog, description="You sad? Use these to at least have a smile!"):
    def __init__(self, bot):
        self.bot = bot
        self.dagpi = {"Authorization": os.getenv("DAGPI")}

    # Say
    @commands.command(name="say", help="Says your text")
    async def say(self, ctx:commands.Context, *, text:str):
        await ctx.reply(F"{text} | {ctx.author.mention}")

    # Sarcasm
    @commands.command(name="sarcasm", help="Says your text in a sarcastic way")
    async def sarcasm(self, ctx:commands.Context, *, text:str):
        await ctx.reply(F"{''.join(c.upper() if i % 2 == 0 else c for i, c in enumerate(text))} | {ctx.author.mention}")

    # PP
    @commands.command(name="pp", help="Tells your or the given user's pp size")
    async def pp(self, ctx:commands.Context, user:discord.User=None):
        user = ctx.author if not user else user
        size = random.randint(1, 35)
        ppmbed = discord.Embed(
            color=self.bot.color,
            title=F"{user.name}'s PP Size:",
            description=F"8{'='*size}D ({size}cm)",
            timestamp=ctx.message.created_at
        )
        ppmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=ppmbed)

    # Ship
    @commands.command(name="ship", aliases=["sp"], help="Ships you or the given member with the other given member")
    async def ship(self, ctx:commands.Context, member1:discord.Member, member2:discord.Member=None):
        spmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        spmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if member2: spmbed.title = F"Shipping {member1} with {member2}"
        else: spmbed.title = F"Shipping {ctx.author} with {member1}"
        number = random.randint(1, 100)
        if number < 25:  spmbed.description = F"`{number}%` - Can't see any love 💔"
        elif number >= 25 and number < 50:  spmbed.description = F"`{number}%` - Can see a sparkle 💖"
        elif number >= 50 and number <= 75:  spmbed.description = F"`{number}%` - I can see pumping 💓"
        elif number > 75:  spmbed.description = F"`{number}%` - CanI can see a lot of love 💘"
        await ctx.reply(embed=spmbed)

    # Counter
    @commands.command(name="counter", aliases=["ctr"], help="Starts an counter")
    async def counter(self, ctx:commands.Context):
        ctrmbed = discord.Embed(
            color=self.bot.color,
            description="Click the button for counting",
            timestamp=ctx.message.created_at
        )
        ctrmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = CounterView(ctx)
        view.message = await ctx.reply(embed=ctrmbed, view=view)

    # Nitro
    @commands.command(name="nitro", help="Gifts free Nitro")
    async def nitro(self, ctx:commands.Context):
        bnitrombed = discord.Embed(
            color=self.bot.color,
            title="A WILD NITRO GIFT APPEARS?!",
            description="Expires in 48 hours\nClick the button for claiming Nitro:.",
            timestamp=ctx.message.created_at
        )
        bnitrombed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = NitroView(ctx)
        view.message = await ctx.reply(embed=bnitrombed, view=view)

    # Token
    @commands.command(name="token", aliases=["tn"], help="Sends an random token")
    async def token(self, ctx:commands.Context):
        session = await self.bot.session.get("https://some-random-api.ml/bottoken")
        response = await session.json()
        session.close()
        tnmbed = discord.Embed(
            color=self.bot.color,
            title="Here is your token",
            description=response['token'],
            timestamp=ctx.message.created_at
        )
        tnmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=tnmbed)

    # Meme
    @commands.command(name="meme", aliases=["me"], help="Shows a random meme")
    async def meme(self, ctx:commands.Context):
        session = await self.bot.session.get("https://some-random-api.ml/meme")
        response = await session.json()
        session.close()
        membed = discord.Embed(
            color=self.bot.color,
            title="Here is a random meme for you",
            description=F"{response['caption']} - {response['category'].title()}",
            timestamp=ctx.message.created_at
        )
        membed.set_image(url=response['image'])
        membed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=membed)

    # Quote
    @commands.command(name="quote", aliases=["qe"], help="Tells you a random quote")
    async def quote(self, ctx:commands.Context):
        mode = random.choice(["quotes", "today", "author", "random"])
        session = await self.bot.session.get(F"https://zenquotes.io/api/{mode}")
        response = await session.json(content_type=None)
        session.close()
        qembed = discord.Embed(
            color=self.bot.color,
            title="Here is a random quote",
            description=F"**Quote:** {response[0]['q']}\n**Author:** {response[0]['a']}",
            timestamp=ctx.message.created_at
        )
        qembed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=qembed)

    # Fact
    @commands.command(name="fact", aliases=["fc"], help="Tells you a random fact")
    async def fact(self, ctx:commands.Context):
        session = await self.bot.session.get("https://api.dagpi.xyz/data/fact", headers=self.dagpi)
        response = await session.json()
        session.close()
        fcmbed = discord.Embed(
            color=self.bot.color,
            title="Here is a random fact",
            description=response["fact"],
            timestamp=ctx.message.created_at
        )
        fcmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=fcmbed)

    # Joke
    @commands.command(name="joke", aliases=["jk"], help="Tells you a random joke")
    async def joke(self, ctx:commands.Context):
        session = await self.bot.session.get("https://api.dagpi.xyz/data/joke", headers=self.dagpi)
        response = await session.json()
        session.close()
        jkmbed = discord.Embed(
            color=self.bot.color,
            title="Here is a random joke",
            description=response["joke"],
            timestamp=ctx.message.created_at
        )
        jkmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=jkmbed)

    # 8Ball
    @commands.command(name="8ball", aliases=["8b"], help="Gives you a random answer for your given question")
    async def _8ball(self, ctx:commands.Context, *, question:str):
        session = await self.bot.session.get("https://api.dagpi.xyz/data/8ball", headers=self.dagpi)
        response = await session.json()
        session.close()
        _8bmbed = discord.Embed(
            color=self.bot.color,
            title="Here is your answer",
            description=F"**Question:** {question}\n**Answer:** {response['response']}",
            timestamp=ctx.message.created_at
        )
        _8bmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=_8bmbed)

    # Roast
    @commands.command(name="roast", aliases=["rt"], help="Roasts you or the given user")
    async def roast(self, ctx:commands.Context, user:discord.User=None):
        user = ctx.author if not user else user
        session = await self.bot.session.get("https://api.dagpi.xyz/data/roast", headers=self.dagpi)
        response = await session.json()
        session.close()
        rtmbed = discord.Embed(
            color=self.bot.color,
            title=F"Roasting {user}",
            description=response['roast'],
            timestamp=ctx.message.created_at
        )
        rtmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=rtmbed)

    # Tweet
    @commands.command(name="tweet", aliases=["tw"], help="Sends a preview from you or the given user with the given text")
    @commands.bot_has_guild_permissions(attach_files=True)
    async def tweet(self, ctx:commands.Context, user:typing.Optional[discord.User]=None, *, text:str):
        user = ctx.author if not user else user
        session = await self.bot.session.get(F"https://api.dagpi.xyz/image/tweet/?url={user.avatar.with_format('png')}&username={user.name}&text={text}", headers=self.dagpi)
        response = io.BytesIO(await session.read())
        session.close()
        twmbed = discord.Embed(
            color=self.bot.color,
            title=F"{user.name}'s tweet",
            timestamp=ctx.message.created_at
        )
        twmbed.set_image(url="attachment://tweet.png")
        twmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(file=discord.File(fp=response, filename="tweet.png"), embed=twmbed)

def setup(bot):
    bot.add_cog(Fun(bot))