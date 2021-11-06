import discord, pomice, re
from discord.ext import commands

URL_REG = re.compile(r"https?://(?:www\.)?.+")

class Music(commands.Cog, description="Jamming out with these!"):
    def __init__(self, bot):
        self.bot = bot
        self.pomice = pomice.NodePool()

    async def start_nodes(self):
        await self.pomice.create_node(bot=self.bot, host="127.0.0.1", port="3030", password="youshallnotpass", identifier="MAIN")
        print(F"Node is ready!")

    # Join
    @commands.command(name="join", aliases=["jn"], help="Joins a voice channel")
    async def join(self, ctx:commands.Context):
        if not ctx.author.voice:
            return await ctx.send("You must be in a voice channel")
        if not ctx.guild.voice_client:
            await ctx.author.voice.channel.connect(cls=pomice.Player)
            return await ctx.send(F"Joined the voice channel {ctx.author.voice.channel.mention}")
        await ctx.send("I'm already in a voice channel")

    # Disconnect
    @commands.command(name="disconnect", aliases=["dc"], help="Disconnects from the voice channel")
    async def disconnect(self, ctx:commands.Context):
        if ctx.guild.voice_client:
            if ctx.me.voice == ctx.author.voice:
                await ctx.guild.voice_client.disconnect()
                return await ctx.send("Disconnected from the voice channel")
            return await ctx.send("Someone else is listening to me")
        await ctx.send("I'm not in a voice channel")

    # Play
    @commands.command(name="play", aliases=["p"], help="Plays a song with the given search term")
    async def play(self, ctx:commands.Context, *, search:str):
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        player = ctx.voice_client
        results = await player.get_tracks(query=f"{search}")
        if not results:
            return await ctx.send("No results were found for that search term.")
        if isinstance(results, pomice.Playlist):
            return await player.play(track=results.tracks[0])
        await player.play(track=results[0])

def setup(bot):
    bot.add_cog(Music(bot))