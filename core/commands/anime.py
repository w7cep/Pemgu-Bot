import discord
from discord.ext import commands
from core.utils.pagination import Paginator

class Anime(commands.Cog, description="Some Weeb shit?!"):
    def __init__(self, bot):
        self.bot = bot

    # SFW
    @commands.command(name="sfw", help="Sends and random SFW Waifu Image")
    async def sfw(self, ctx:commands.Context):
        session = await self.bot.session.get("https://api.waifu.im/sfw/waifu/")
        response = await session.json()
        session.close()
        sfwmbed = discord.Embed(
            color=self.bot.color,
            url=F"https://waifu.im/preview/?image={response.get('tags')[0].get('images')[0].get('file')}",
            title="Here is your SFW Image",
            timestamp=ctx.message.created_at
        )
        sfwmbed.set_image(url=response.get('tags')[0].get('images')[0].get('url'))
        sfwmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=sfwmbed)
    
    # NSFW
    @commands.command(name="nsfw", help="Sends and random NSFW Waifu Image")
    @commands.is_nsfw()
    async def nsfw(self, ctx:commands.Context):
        session = await self.bot.session.get("https://api.waifu.im/nsfw/ero/")
        response = await session.json()
        session.close()
        nsfwmbed = discord.Embed(
            color=self.bot.color,
            url=F"https://waifu.im/preview/?image={response.get('tags')[0].get('images')[0].get('file')}",
            title="Here is your NSFW Image",
            timestamp=ctx.message.created_at
        )
        nsfwmbed.set_image(url=response.get('tags')[0].get('images')[0].get('url'))
        nsfwmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=nsfwmbed)

def setup(bot):
    bot.add_cog(Anime(bot))