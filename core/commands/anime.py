import discord
from discord.ext import commands

class Anime(commands.Cog, description="Some Weeb shit?!"):
    def __init__(self, bot):
        self.bot = bot

    # Waifu
    @commands.command(name="waifu", help="Sends an random SFW Waifu Image")
    async def waifu(self, ctx:commands.Context):
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
        await ctx.reply(embed=sfwmbed)
    
    # NWaifu
    @commands.command(name="nwaifu", help="Sends an random NSFW Waifu Image")
    @commands.is_nsfw()
    async def nwaifu(self, ctx:commands.Context):
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
        await ctx.reply(embed=nsfwmbed)

def setup(bot):
    bot.add_cog(Anime(bot))
