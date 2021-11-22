import discord
from discord.ext import commands

class OnConnect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_connect(self):
        self.bot.uptime = discord.utils.utcnow()
        oni = [
            F"Logged in as: {self.bot.user} - {self.bot.user.id}",
            F"Main prefix is: {self.bot.default_prefix}",
            F"Servers bot is in: {len(self.bot.guilds)}",
            F"Users bot is seeing: {len(self.bot.users)}",
        ]
        print("\n".join(o for o in oni))

class OnDisconnect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_disconnect(self):
        print(F"Logged off as: {self.bot.user} - {self.bot.user.id}\nDisconnected from discord.")
        if not self.bot.session.closed:
            await self.bot.session.close()

def setup(bot):
    bot.add_cog(OnConnect(bot))
    bot.add_cog(OnDisconnect(bot))