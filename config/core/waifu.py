import discord, os
from discord.ext import commands
from config.utils.aiohttp import session_json

class Anime(commands.Cog, description="SFW Waifu's and Husbando's chamber"):
    def __init__(self, bot):
        self.bot = bot

    # SFW
    @commands.command(name="sfw", help="Will send an random sfw waifu or husbando image if not specified")
    async def sfw(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/sfw/all/")
        sfwmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your SFW Image",
            timestamp=ctx.message.created_at
        )
        sfwmbed.set_image(url=session["url"])
        sfwmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=sfwmbed)

    # Waifu
    @commands.command(name="waifu", aliases=["wa"], help="Will send an random sfw waifu image")
    async def waifu_sfw(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/sfw/waifu/")
        wambed = discord.Embed(
            colour=self.bot.color,
            title="Here is your SFW Waifu Image",
            timestamp=ctx.message.created_at
        )
        wambed.set_image(url=session["url"])
        wambed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=wambed)

    # NSFW
    @commands.command(name="nsfw", help="Will send an random nsfw waifu or husbando image if nor specified")
    @commands.is_nsfw()
    async def nsfw(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/nsfw/ero/")
        nsfwmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your NSFW Image",
            timestamp=ctx.message.created_at
        )
        nsfwmbed.set_image(url=session["url"])
        nsfwmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=nsfwmbed)

    # Ass
    @commands.command(name="ass", help="Will send an random nsfw ass image")
    @commands.is_nsfw()
    async def ass(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/nsfw/ass/")
        assmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your NSFW Ass Image",
            timestamp=ctx.message.created_at
        )
        assmbed.set_image(url=session["url"])
        assmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=assmbed)

    # Ecchi
    @commands.command(name="ecchi", help="Will send an random nsfw ecchi image")
    @commands.is_nsfw()
    async def ecchi(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/nsfw/ecchi/")
        ecchimbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your NSFW Ecchi Image",
            timestamp=ctx.message.created_at
        )
        ecchimbed.set_image(url=session["url"])
        ecchimbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=ecchimbed)

    # Ero
    @commands.command(name="ero", help="Will send an an random nsfw ero image")
    @commands.is_nsfw()
    async def ero(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/nsfw/ero/")
        erombed = discord.Embed(
            colour=self.bot.color,
            title="Here is your NSFW Ero Image",
            timestamp=ctx.message.created_at
        )
        erombed.set_image(url=session["url"])
        erombed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=erombed)

    # Hentai
    @commands.command(name="hentai", help="Will send an random nsfw hentai image")
    @commands.is_nsfw()
    async def hentai(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/nsfw/hentai/")
        hentaimbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your NSFW Hentai Image",
            timestamp=ctx.message.created_at
        )
        hentaimbed.set_image(url=session["url"])
        hentaimbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=hentaimbed)

    # Maid
    @commands.command(name="maid", help="Will send an random nsfw maid image")
    @commands.is_nsfw()
    async def maid(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/nsfw/maid/")
        maidmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your NSFW Maid Image",
            timestamp=ctx.message.created_at
        )
        maidmbed.set_image(url=session["url"])
        maidmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=maidmbed)

    # Milf
    @commands.command(name="milf", help="Will send an random nsfw milf image")
    @commands.is_nsfw()
    async def milf(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/nsfw/milf/")
        milfmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your NSFW Milf Image",
            timestamp=ctx.message.created_at
        )
        milfmbed.set_image(url=session["url"])
        milfmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=milfmbed)

    # Oppai
    @commands.command(name="oppai", help="Will send an random nsfw oppai image")
    @commands.is_nsfw()
    async def oppai(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/nsfw/oppai/")
        oppaimbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your NSFW Oppai Image",
            timestamp=ctx.message.created_at
        )
        oppaimbed.set_image(url=session["url"])
        oppaimbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=oppaimbed)

    # Oral
    @commands.command(name="oral", help="Will send an random nsfw oral image")
    @commands.is_nsfw()
    async def oral(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/nsfw/oral/")
        oralmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your NSFW Oral Image",
            timestamp=ctx.message.created_at
        )
        oralmbed.set_image(url=session["url"])
        oralmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=oralmbed)

    # Paizuri
    @commands.command(name="paizuri", help="Will send an random nsfw paizuri image")
    @commands.is_nsfw()
    async def paizuri(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/nsfw/paizuri/")
        paizurimbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your NSFW Paizuri Image",
            timestamp=ctx.message.created_at
        )
        paizurimbed.set_image(url=session["url"])
        paizurimbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=paizurimbed)

    # Selfies
    @commands.command(name="selfies", help="Will send an random nsfw selfies image")
    @commands.is_nsfw()
    async def selfies(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/nsfw/selfies/")
        selfiesmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your NSFW Selfies Image",
            timestamp=ctx.message.created_at
        )
        selfiesmbed.set_image(url=session["url"])
        selfiesmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=selfiesmbed)

    # Uniform
    @commands.command(name="uniform", help="Will send an random nsfw uniform image")
    @commands.is_nsfw()
    async def uniform(self, ctx):
        await ctx.trigger_typing()
        session = await session_json("https://api.hori.ovh/nsfw/uniform/")
        uniformmbed = discord.Embed(
            colour=self.bot.color,
            title="Here is your NSFW Uniform Image",
            timestamp=ctx.message.created_at
        )
        uniformmbed.set_image(url=session["url"])
        uniformmbed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=uniformmbed)

def setup(bot):
    bot.add_cog(Anime(bot))