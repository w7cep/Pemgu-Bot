import discord, pomice, re, asyncio, os
from discord.ext import commands

URL_REG = re.compile(r"https?://(?:www\.)?.+")

class Music(commands.Cog, description="Jamming out with these!"):
    def __init__(self, bot):
        self.bot = bot
        self.pomice = pomice.NodePool()

    async def start_nodes(self):
        await self.pomice.create_node(bot=self.bot, host="lavalink.darrennathanael.com", port="80", password="clover", identifier="MAIN", spotify_client_id=os.getenv("SPOTIFY").split(", ")[0], spotify_client_secret=os.getenv("SPOTIFY").split(", ")[1])
        print("Created a node")

    # Join
    @commands.command(name="join", aliases=["jn"], help="Joins a voice channel")
    @commands.guild_only()
    async def join(self, ctx:commands.Context):
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect(cls=pomice.Player)
            ctx.voice_client.queue = asyncio.Queue()
            return await ctx.send(F"Joined the voice channel {ctx.author.voice.channel.mention}")
        await ctx.send("I'm already in a voice channel")

    # Disconnect
    @commands.command(name="disconnect", aliases=["dc"], help="Disconnects from the voice channel")
    @commands.guild_only()
    async def disconnect(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.me.voice.channel == ctx.author.voice.channel:
                if not ctx.voice_client.queue.empty():
                    for _ in range(ctx.voice_client.queue.qsize()):
                        ctx.voice_client.queue.get_nowait()
                        ctx.voice_client.queue.task_done()
                    await ctx.send("Cleared the queue")
                await ctx.voice_client.destroy()                    
                return await ctx.send("Disconnected from the voice channel")
            return await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")
        await ctx.send("I'm not in a voice channel")

    # Play
    @commands.command(name="play", aliases=["p"], help="Plays music with the given search term")
    @commands.guild_only()
    async def play(self, ctx:commands.Context, *, search:str):
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        if ctx.me.voice.channel == ctx.author.voice.channel:
            results = await ctx.voice_client.get_tracks(query=search)
            if not results:
                return await ctx.send("No results were found for that search term.")
            if isinstance(results, pomice.Playlist):
                for track in results.tracks:
                    await ctx.voice_client.queue.put(track)
            else:
                await ctx.voice_client.queue.put(results[0])
            if not ctx.voice_client.is_playing:
                song = await ctx.voice_client.get_tracks(query=(await ctx.voice_client.queue.get()).title)
                if isinstance(song, pomice.Playlist):
                    await ctx.voice_client.play(track=song.tracks[0])
                else:
                    await ctx.voice_client.play(track=song[0])
                    return await ctx.send(F"Now playing: {ctx.voice_client.current.title}\nBy: {ctx.voice_client.current.author}\nRequested: {ctx.author.mention}\nURL: {ctx.voice_client.current.uri}")
            else:
                return await ctx.send(F"Added {search.title()} to the queue")
        return await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")

    # Next
    @commands.command(name="next", aliases=["nx"], help="Plays the next song in the queue")
    @commands.guild_only()
    async def next(self, ctx:commands.Context):
        if not ctx.voice_client:
            await ctx.send("No one is using to me")
        if ctx.voice_client.queue.empty():
            return await ctx.send("There is nothing in the queue")
        if ctx.me.voice.channel == ctx.author.voice.channel:
            results = await ctx.voice_client.get_tracks(query=(await ctx.voice_client.queue.get()).title)
            await ctx.voice_client.stop()
            if isinstance(results, pomice.Playlist):
                await ctx.voice_client.play(track=results.tracks[0])
            else:
                await ctx.voice_client.play(track=results[0])
            return await ctx.send(F"Now playing: {ctx.voice_client.current.title}\nBy: {ctx.voice_client.current.author}\nRequested: {ctx.author.mention}\nURL: {ctx.voice_client.current.uri}")
        return await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")

    # Resume
    @commands.command(name="resume", aliases=["ru"], help="Resumes the paused music")
    @commands.guild_only()
    async def resume(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.me.voice == ctx.author.voice:
                if ctx.voice_client.is_paused:
                    await ctx.voice_client.set_pause(pause=False)
                    return await ctx.send("Resumed the music")
                elif ctx.voice_client.is_playing:
                    return await ctx.send("The music is already playing")
            return await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")
        await ctx.send("No one is using to me")

    # Pause
    @commands.command(name="pause", aliases=["pu"], help="Pauses playing music")
    @commands.guild_only()
    async def pause(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.me.voice == ctx.author.voice:
                if ctx.voice_client.is_paused:
                    return await ctx.send("Music is already paused")
                elif ctx.voice_client.is_playing:
                    await ctx.voice_client.set_pause(pause=True)
                    return await ctx.send("Paused the music")
            return await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")
        await ctx.send("No one is using to me")

    # Volume
    @commands.command(name="volume", aliases=["vol"], help="Sets the volume of the music")
    @commands.guild_only()
    async def volume(self, ctx:commands.Context, *, volume:int):
        if ctx.voice_client:
            if ctx.me.voice == ctx.author.voice:
                if volume < 0 or volume > 500:
                    return await ctx.send("The volume must be between 0 and 500")
                await ctx.voice_client.set_volume(volume)
                return await ctx.send(F"Set the volume to {volume}")
            return await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")
        await ctx.send("No one is using to me")

def setup(bot):
    bot.add_cog(Music(bot))