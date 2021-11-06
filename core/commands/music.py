import discord, pomice, re
from discord.ext import commands

URL_REG = re.compile(r"https?://(?:www\.)?.+")

class Music(commands.Cog, description="Jamming out with these!"):
    def __init__(self, bot):
        self.bot = bot
        self.pomice = pomice.NodePool()

    async def start_nodes(self):
        await self.pomice.create_node(bot=self.bot, host="lavalink.darrennathanael.com", port="80", password="clover", identifier="MAIN", spotify_client_id=None, spotify_client_secret=None)
        print("Created a node")

    # Join
    @commands.command(name="join", aliases=["jn"], help="Joins a voice channel")
    @commands.guild_only()
    async def join(self, ctx:commands.Context):
        if not ctx.author.voice:
            return await ctx.send("You must be in a voice channel")
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect(cls=pomice.Player)
            return await ctx.send(F"Joined the voice channel {ctx.author.voice.channel.mention}")
        await ctx.send("I'm already in a voice channel")

    # Disconnect
    @commands.command(name="disconnect", aliases=["dc"], help="Disconnects from the voice channel")
    @commands.guild_only()
    async def disconnect(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.me.voice.channel == ctx.author.voice.channel:
                await ctx.voice_client.disconnect()
                return await ctx.send("Disconnected from the voice channel")
            return await ctx.send("Someone else is using to me")
        await ctx.send("I'm not in a voice channel")

    # Play
    @commands.command(name="play", aliases=["p"], help="Plays music with the given search term")
    @commands.guild_only()
    async def play(self, ctx:commands.Context, *, search:str):
        if not ctx.author.voice:
            return await ctx.send("You must be in a voice channel")
        if not ctx.voice_client:
            await ctx.invoke(self.join)
            results = await ctx.voice_client.get_tracks(query=search)
            info = ctx.voice_client.current.info
            print(results)
            if not results:
                return await ctx.send("No results were found for that search term.")
            if isinstance(results, pomice.Playlist):
                return await ctx.voice_client.play(track=results.tracks[0])
            await ctx.voice_client.play(track=results[0])
            return await ctx.send(F"Now playing: {info.get('title')}\nBy: {info.get('author')}\nRequested: {info.get('requester')}\nURL:{info.get('url')}")
        return await ctx.send("Someone else is using to me")

    # Stop
    @commands.command(name="stop", aliases=["so"], help="Stops playing music")
    @commands.guild_only()
    async def stop(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.voice_client.is_paused() == True:
                if ctx.voice_client.channel == ctx.author.voice.channel:
                    await ctx.voice_client.resume()
                    return await ctx.send("Resumed the music")
                return await ctx.send("Someone else is using to me")
            return await ctx.send("I'm not paused")
        await ctx.send("The music is not paused")

    # Resume
    @commands.command(name="resume", aliases=["ru"], help="Resumes the paused music")
    @commands.guild_only()
    async def resume(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.voice_client.is_paused() == True:
                if ctx.voice_client.channel == ctx.author.voice.channel:
                    await ctx.voice_client.resume()
                    return await ctx.send("Resumed the music")
                return await ctx.send("Someone else is using to me")
            return await ctx.send("Music is not paused")
        await ctx.send("No one is using to me")

    # Pause
    @commands.command(name="pause", aliases=["pu"], help="Pauses playing music")
    @commands.guild_only()
    async def pause(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.voice_client.is_playing() == True:
                if ctx.voice_client.channel == ctx.author.voice.channel:
                    await ctx.voice_client.pause()
                    return await ctx.send("Paused the music")
                return await ctx.send("Someone else is using to me")
            return await ctx.send("Nothing is playing")
        await ctx.send("No one is using to me")

def setup(bot):
    bot.add_cog(Music(bot))