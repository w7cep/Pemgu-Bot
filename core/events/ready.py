import discord
from discord.ext import commands

class OnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.uptime = discord.utils.utcnow()
        ori = [
            F"Logged in as: {self.bot.user} - {self.bot.user.id}",
            F"Main prefix is: {self.bot.default_prefix}",
            F"Servers bot is in: {len(self.bot.guilds)}",
            "The Bot is online now"
        ]
        print("\n".join(o for o in ori))
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=F"{len(self.bot.guilds)} and {len(self.bot.users)}"))

def setup(bot):
    bot.add_cog(OnReady(bot))