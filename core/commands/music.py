import discord, pomice, re
from discord.ext import commands

URL_REG = re.compile(r"https?://(?:www\.)?.+")

class Music(commands.Cog, description="Jamming out with these!"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.queue = {}
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
                queue = self.bot.queue.get(str(ctx.guild.id))
                if queue:
                    del self.bot.queue[str(ctx.guild.id)]
                    return await ctx.send("Cleared queue")
                await ctx.voice_client.destroy()                    
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
        if ctx.me.voice.channel == ctx.author.voice.channel:
            self.bot.queue[str(ctx.guild.id)] = []
            results = await ctx.voice_client.get_tracks(query=search)
            if not results:
                return await ctx.send("No results were found for that search term.")
            if not ctx.voice_client.is_playing:
                if isinstance(results, pomice.Playlist):
                    await ctx.voice_client.play(track=results.tracks[0])
                else:
                    await ctx.voice_client.play(track=results[0])
                return await ctx.send(F"Now playing: {ctx.voice_client.current.title}\nBy: {ctx.voice_client.current.author}\nRequested: {ctx.author.mention}\nURL: {ctx.voice_client.current.uri}")
            if isinstance(results, pomice.Playlist):
                self.bot.queue[str(ctx.guild.id)].append(results.tracks[0])
            else:
                self.bot.queue[str(ctx.guild.id)].append(results[0])
            return await ctx.send(F"Added {results[0].title} to the queue")
        return await ctx.send("Someone else is using to me")

    # Next
    @commands.command(name="next", aliases=["nx"], help="Plays the next song in the queue")
    @commands.guild_only()
    async def next(self, ctx:commands.Context):
        if not ctx.author.voice:
            return await ctx.send("You must be in a voice channel")
        if not ctx.voice_client:
            await ctx.send("No one is using to me")
        search = self.bot.queue.get(str(ctx.guild.id))
        if not search:
            return await ctx.send("There is nothing in the queue")
        if ctx.me.voice.channel == ctx.author.voice.channel:
            results = await ctx.voice_client.get_tracks(query=search[0].title)
            if isinstance(results, pomice.Playlist):
                await ctx.voice_client.play(track=results.tracks[0])
            else:
                await ctx.voice_client.play(track=results[0])
            del self.bot.queue[str(ctx.guild.id)][0]
            return await ctx.send(F"Now playing: {ctx.voice_client.current.title}\nBy: {ctx.voice_client.current.author}\nRequested: {ctx.author.mention}\nURL: {ctx.voice_client.current.uri}")
        return await ctx.send("Someone else is using to me")

    # Resume
    @commands.command(name="resume", aliases=["ru"], help="Resumes the paused music")
    @commands.guild_only()
    async def resume(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                if not ctx.voice_client.is_paused:
                    return await ctx.send("Music is not paused")
                await ctx.voice_client.set_pause(pause=False)
                return await ctx.send("Resumed the music")
            return await ctx.send("Someone else is using to me")
        await ctx.send("No one is using to me")

    # Pause
    @commands.command(name="pause", aliases=["pu"], help="Pauses playing music")
    @commands.guild_only()
    async def pause(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                if not ctx.voice_client.is_playing:
                    return await ctx.send("Nothing is getting played")
                await ctx.voice_client.set_pause(pause=True)
                return await ctx.send("Paused the music")
            return await ctx.send("Someone else is using to me")
        await ctx.send("No one is using to me")

def setup(bot):
    bot.add_cog(Music(bot))