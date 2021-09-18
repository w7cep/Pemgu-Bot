import discord, os, io
from discord.ext import commands

class API(commands.Cog, description="Some cool commands that uses internet"):
    def __init__(self, bot):
        self.bot = bot
        headers=self.dagpi_headers = {
            "Authorization": os.getenv("DAGPI")
        }
    
    # Joke
    @commands.command(name="joke", aliases=["jk"], help="Will tell you a random joke")
    async def joke(self, ctx):
        await ctx.trigger_typing()
        async with self.bot.aiosession.get("https://api.dagpi.xyz/data/joke", headers=self.dagpi_headers) as response:
            response = await response.json()
        jkmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is a random joke",
            description=response["joke"],
            timestamp=ctx.message.created_at
        )
        jkmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=jkmbed)

    # 8Ball
    @commands.command(name="8ball", aliases=["8b"], help="Will give you a random answer", usage="<question>")
    async def _8ball(self, ctx, *, question):
        await ctx.trigger_typing()
        async with self.bot.aiosession.get("https://api.dagpi.xyz/data/8ball", headers=self.dagpi_headers) as response:
            response = await response.json()
        _8bmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your answer",
            timestamp=ctx.message.created_at
        )
        _8bmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        _8bmbed.add_field(name="Your Question:", value=question)
        _8bmbed.add_field(name="Your Answer:", value=response["response"])
        await ctx.send(embed=_8bmbed)

    # Pixel
    @commands.command(name="pixel", aliases=["pxl"], help="Will make the given image pixelated", usage="[user]")
    @commands.bot_has_guild_permissions(attach_files=True)
    async def pixel(self, ctx, user:commands.UserConverter = None):
        await ctx.trigger_typing()
        user = user or ctx.author
        async with self.bot.aiosession.get(F"https://api.dagpi.xyz/image/pixel/?url={user.avatar.with_static_format('png').with_size(1024)}", headers=self.dagpi_headers) as response:
            response = await io.BytesIO(await response.read())
        pxlmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is the pixelated for the image",
            timestamp=ctx.message.created_at
        )
        pxlmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        pxlmbed.set_image(url="attachment://pixel.png")
        await ctx.send(file=discord.File(response, filename="pixel.png"), embed=pxlmbed)

    # Colors
    @commands.command(name="colors", aliases=["clrs"], help="Will give you the colors from the given image", usage="[user]")
    @commands.bot_has_guild_permissions(attach_files=True)
    async def colors(self, ctx, user:commands.UserConverter = None):
        await ctx.trigger_typing()
        user = user or ctx.author
        async with self.bot.aiosession.get(F"https://api.dagpi.xyz/image/colors/?url={user.avatar.with_static_format('png').with_size(1024)}", headers=self.dagpi_headers) as response:
            response = await io.BytesIO(await response.read())
        clrsmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is the colors for the image",
            timestamp=ctx.message.created_at
        )
        clrsmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        clrsmbed.set_image(url="attachment://colors.png")
        await ctx.send(file=discord.File(response, filename="colors.png"), embed=clrsmbed)

    # Tweet
    @commands.command(name="tweet", aliases=["tw"], help="Will preview your tweet", usage="<username> <text>")
    @commands.bot_has_guild_permissions(attach_files=True)
    async def tweet(self, ctx, *, text, user:commands.UserConverter = None):
        await ctx.trigger_typing()
        user = user or ctx.author
        async with self.bot.aiosession.get(F"https://api.dagpi.xyz/image/tweet/?url={user.avatar.with_static_format('png').with_size(1024)}&username={ctx.author.name}&text={text}", headers=self.dagpi_headers) as response:
            response = await io.BytesIO(await response.read())
        twmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your tweet's preview",
            timestamp=ctx.message.created_at
        )
        twmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        twmbed.set_image(url="attachment://tweet.png")
        await ctx.send(file=discord.File(response, filename="tweet.png"), embed=twmbed)

    # Screenshot
    @commands.command(name="screenshot", aliases=["ss"], help="Will give you a preview from the given website", usage="<website>")
    @commands.bot_has_guild_permissions(attach_files=True)
    async def screenshot(self, ctx, *, website):
        await ctx.trigger_typing()
        async with self.bot.aiosession.get(F"https://api.screenshotmachine.com?key=a95edd&url={website}&dimension=1024x768") as response:
            response = await io.BytesIO(await response.read())
        ssmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your screenshot",
            timestamp=ctx.message.created_at
        )
        ssmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        ssmbed.set_image(url="attachment://screenshot.png")
        await ctx.send(file=discord.File(response, filename="screenshot.png"), embed=ssmbed)

    # Pypi
    @commands.command(name="pypi", help="Will give information about the given lib in pypi")
    async def pypi(self, ctx, *, lib):
        await ctx.trigger_typing()
        async with self.bot.aiosession.get(F"https://pypi.org/pypi/{lib}/json") as response:
            if response.status != 200:
                await ctx.send("Couldn't find that library in PYPI")
                return
            response = await response.json()
        pypimbed = discord.Embed(
            colour=self.bot.color,
            url=response['info']['package_url'],
            title=response['info']['name'],
            description=response['info']['summary'],
            timestamp=ctx.message.created_at
        )
        pypimbed.add_field(name="Author Info:", value=F"Name: {response['info']['author']}\nEmail:{response['info']['author_email']}", inline=False)
        pypimbed.add_field(name="Package Info:", value=F"""**Version:** {response['info']['version']}
            **Download URL:** {response['info']['download_url']}
            **Documentation URL:** {response['info']['docs_url']}
            **Home Page:** {response['info']['home_page']}
            **Yanked:** {response['info']['yanked']} - {response['info']['yanked_reason']}
            **Keywords:** {response['info']['keywords']}
            **License:** {response['info']['license']}""", inline=False)
        pypimbed.add_field(name="Classifiers:", value=",\n    ".join(classifier for classifier in response['info']['classifiers']), inline=False)
        pypimbed.set_thumbnail(url="https://cdn.discordapp.com/attachments/873478114183880704/887470965188091944/pypilogo.png")
        pypimbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=pypimbed)

def setup(bot):
    bot.add_cog(API(bot))
