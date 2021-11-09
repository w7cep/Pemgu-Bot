import discord, pomice, re, os, asyncio
from discord.ext import commands

URL_REG = re.compile(r"https?://(?:www\.)?.+")

class ViewMusic(discord.ui.View):
    def __init__(self, ctx, music):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.music = music

    @discord.ui.button(label="Resume", style=discord.ButtonStyle.green)
    async def resume(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_paused:
            await interaction.response.send_message(F"Resumed: {self.ctx.voice_client.current.title} | {self.ctx.voice_client.current.author}", ephemeral=True)
            return await self.ctx.voice_client.set_pause(pause=False)
        await interaction.response.send_message(F"Resume: already on resume, {self.ctx.voice_client.current.title} | {self.ctx.voice_client.current.author}", ephemeral=True)

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.green)
    async def pause(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing:
            await interaction.response.send_message(F"Paused: {self.ctx.voice_client.current.title} | {self.ctx.voice_client.current.author}", ephemeral=True)
            return await self.ctx.voice_client.set_pause(pause=True)
        await interaction.response.send_message(F"Pause: already on pause, {self.ctx.voice_client.current.title} | {self.ctx.voice_client.current.author}", ephemeral=True)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red)
    async def stop(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            if not self.ctx.voice_client.queue.empty():
                for _ in range(self.ctx.voice_client.queue.qsize()):
                    self.ctx.voice_client.queue.get_nowait()
                    self.ctx.voice_client.queue.task_done()
                for _ in range(len(self.ctx.voice_client.lqueue)):
                    self.ctx.voice_client.lqueue.pop(0)
            await interaction.response.send_message(F"Stopped: {self.ctx.voice_client.current.title} - {self.ctx.voice_client.current.author}", ephemeral=True)
            return await self.ctx.voice_client.stop()
        return await interaction.response.send_message("Stop - Nothing is playing", ephemeral=True)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.blurple)
    async def skip(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            if not self.ctx.voice_client.queue.empty():
                await interaction.response.send_message(F"Skipped: {self.ctx.voice_client.current.title} | {self.ctx.voice_client.current.author}", ephemeral=True)
                return await self.ctx.voice_client.stop()
            return await interaction.response.send_message("Skip - There is nothing in the queue", ephemeral=True)
        return await interaction.response.send_message("Skip - Nothing is playing", ephemeral=True)

    async def nowplaying(self, interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            npmbed = discord.Embed(
                color=self.music.color,
                url=self.ctx.voice_client.current.uri,
                title=F"Playing:\n{self.ctx.voice_client.current.title}",
                description=F"By: {self.ctx.voice_client.current.author}\nRequested by {self.ctx.voice_client.current.requester.mention}\nDuration: {'%d:%d:%d'%((self.ctx.voice_client.current.length/(1000*60*60))%24, (self.ctx.voice_client.current.length/(1000*60))%60, (self.ctx.voice_client.current.length/1000)%60)}",
                timestamp=self.ctx.voice_client.current.ctx.message.created_at
            )
            npmbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=npmbed, view=self, ephemeral=True)
        return await interaction.response.send_message.send("Nothing is playing", ephemeral=True)


    @discord.ui.button(label="Queue", style=discord.ButtonStyle.blurple)
    async def queue(self, button:discord.ui.Button, interaction:discord.Interaction):
        if len(self.ctx.voice_client.lqueue) > 1:
            d = "\n".join(q for q in self.ctx.voice_client.lqueue)
            qumbed = discord.Embed(
                color=self.music.color,
                title="Queue",
                description=self.ctx.bot.trim(d, 4095),
                timestamp=self.ctx.message.created_at
            )
            qumbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=qumbed, ephemeral=True)
        return await self.nowplaying(interaction=interaction)

    @discord.ui.button(label="Lyrics", style=discord.ButtonStyle.grey)
    async def lyrics(self, button:discord.ui.Button, interaction:discord.Interaction):
        lyrics = await self.ctx.bot.openrobot.lyrics(self.ctx.voice_client.current.title)
        lymbed = discord.Embed(
            color=self.music.color,
            title=lyrics.title,
            description=self.ctx.bot.trim(lyrics.lyrics, 4096),
            timestamp=self.ctx.message.created_at
        )
        lymbed.set_thumbnail(url=lyrics.images.track or discord.Embed.Empty)
        lymbed.set_author(name=lyrics.artist, icon_url=lyrics.images.background or discord.Embed.Empty)
        lymbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=lymbed,  ephemeral=True)

    async def interaction_check(self, interaction:discord.Interaction):
        for member in self.ctx.me.voice.channel.members:
            if interaction.user.id == member.id:
                return True
        icheckmbed = discord.Embed(
            color=self.music.color,
            title=F"You can't use this",
            description=F"<@{interaction.user.id}> - Only <@{self.ctx.message.author.id}> can use this\nCause they did the command\nIf you want to use this, do what they did",
            timestamp=interaction.message.created_at
        )
        icheckmbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=icheckmbed, ephemeral=True)
        return False

class Music(commands.Cog, description="Jamming out with these!"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.pomice = pomice.NodePool()
        self.color = 0x1DB954

    async def create_node_pomice(self):
        await self.bot.pomice.create_node(bot=self.bot, host="lavalink.darrennathanael.com", port="80", password="clover", identifier="Pomice", spotify_client_id=os.getenv("SPOTIFY").split(", ")[0], spotify_client_secret=os.getenv("SPOTIFY").split(", ")[1])
        print("Created a Pomice Node")

    # Join
    @commands.command(name="join", aliases=["jn"], help="Joins a voice channel")
    @commands.guild_only()
    async def join(self, ctx:commands.Context):
        if not ctx.me.voice:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect(cls=pomice.Player)
                ctx.voice_client.queue = asyncio.Queue()
                ctx.voice_client.lqueue = []
                return await ctx.send(F"Joined the voice channel {ctx.author.voice.channel.mention}")
            return await ctx.send("You must be in a voice channel")
        await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")

    # Disconnect
    @commands.command(name="disconnect", aliases=["dc"], help="Disconnects from the voice channel")
    @commands.guild_only()
    async def disconnect(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.author.voice:
                if ctx.me.voice.channel == ctx.author.voice.channel:
                    await ctx.voice_client.destroy()                    
                    return await ctx.send("Disconnected from the voice channel")
                return await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")
            return await ctx.send("You must be in a voice channel")
        await ctx.send("I'm not in a voice channel")

    # Play
    @commands.command(name="play", aliases=["p"], help="Plays music with the given term, term can be a url or a query or a playlist")
    @commands.guild_only()
    async def play(self, ctx:commands.Context, *, term:str):
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        if not ctx.author.voice:
            return await ctx.send("You must be in a voice channel")
        if ctx.me.voice.channel == ctx.author.voice.channel:
            results = await ctx.voice_client.get_tracks(query=term, ctx=ctx)
            print(results)
            if not results:
                return await ctx.send("No results were found for that search term.")
            if isinstance(results, pomice.Playlist):
                for track in results.tracks:
                    await ctx.voice_client.queue.put(track)
                    ctx.voice_client.lqueue.append(F"{track.title} - {track.author}")
            elif isinstance(results, pomice.Track):
                await ctx.voice_client.queue.put(results.title)
                ctx.voice_client.lqueue.append(F"{results.title} - {results.author}")
            else:
                await ctx.voice_client.queue.put(results[0])
                ctx.voice_client.lqueue.append(F"{results[0].title} - {results[0].author}")
            if not ctx.voice_client.is_playing:
                return await ctx.voice_client.play(track=(await ctx.voice_client.queue.get()))
            else:
                return await ctx.send(F"Added {results if isinstance(results, pomice.Playlist) else results[0]} to the queue")
        return await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")

    # Stop
    @commands.command(name="stop", aliases=["so"], help="Stops playing and Clears queue")
    @commands.guild_only()
    async def stop(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.author.voice:
                if ctx.me.voice.channel == ctx.author.voice.channel:
                    if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
                        for _ in range(ctx.voice_client.queue.qsize()):
                            ctx.voice_client.queue.get_nowait()
                            ctx.voice_client.queue.task_done()
                        await ctx.send(F"Stopped: {ctx.voice_client.current.title} - {ctx.voice_client.current.author}")
                        return await ctx.voice_client.stop()
                    return await ctx.send("Nothing is playing")
                return await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")
            return await ctx.send("You must be in a voice channel")
        await ctx.send("I'm not in a voice channel")

    # Skip
    @commands.command(name="skip", aliases=["sk"], help="Skips the music")
    @commands.guild_only()
    async def skip(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.author.voice:
                if ctx.me.voice.channel == ctx.author.voice.channel:
                    if ctx.voice_client.is_playing:
                        if not ctx.voice_client.queue.empty():
                            await ctx.send(F"Skipped: {ctx.voice_client.current.title} | {ctx.voice_client.current.author}")
                            return await ctx.voice_client.stop()
                        return await ctx.send("There is nothing in the queue")
                    return await ctx.send("Nothing is playing")
                return await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")
            return await ctx.send("You must be in a voice channel")
        await ctx.send("I'm not in a voice channel")

    # Resume
    @commands.command(name="resume", aliases=["ru"], help="Resumes the paused music")
    @commands.guild_only()
    async def resume(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.author.voice:
                if ctx.me.voice.channel == ctx.author.voice.channel:
                    if ctx.voice_client.is_paused:
                        await ctx.voice_client.set_pause(pause=False)
                        return await ctx.send("Resumed the music")
                    return await ctx.send("The music is already playing")
                return await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")
            return await ctx.send("You must be in a voice channel")
        await ctx.send("I'm not in a voice channel")

    # Pause
    @commands.command(name="pause", aliases=["pu"], help="Pauses playing music")
    @commands.guild_only()
    async def pause(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.author.voice:
                if ctx.me.voice.channel == ctx.author.voice.channel:
                    if ctx.voice_client.is_playing:
                        await ctx.voice_client.set_pause(pause=True)
                        return await ctx.send("Paused the music")
                    return await ctx.send("Music is already paused")
                return await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")
            return await ctx.send("You must be in a voice channel")
        await ctx.send("I'm not in a voice channel")

    # Volume
    @commands.command(name="volume", aliases=["vol"], help="Sets or Tells the volume of the music")
    @commands.guild_only()
    async def volume(self, ctx:commands.Context, *, volume:int=None):
        if ctx.voice_client:
            if ctx.author.voice:
                if ctx.me.voice.channel == ctx.author.voice.channel:
                    if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
                        if volume:
                            if not volume < 0 or not volume > 500:
                                await ctx.voice_client.set_volume(volume)
                                return await ctx.send(F"Set the volume to {volume}")
                            return await ctx.send("The volume must be between 0 and 500")
                        return await ctx.send(F"The volume is currently at {ctx.voice_client.volume}")
                    return await ctx.send("Nothing is playing")
                return await ctx.send(F"Someone else is using to me in {ctx.me.voice.channel.mention}")
            return await ctx.send("You must be in a voice channel")
        await ctx.send("I'm not in a voice channel")

    # Queue
    @commands.command(name="queue", aliases=["qu"], help="Shows the queue")
    @commands.guild_only()
    async def queue(self, ctx:commands.Context):
        if ctx.voice_client:
            if len(ctx.voice_client.lqueue) > 1:
                d = "\n".join(q for q in ctx.voice_client.lqueue)
                qumbed = discord.Embed(
                    color=self.color,
                    title="Queue",
                    description=self.bot.trim(d, 4095),
                    timestamp=ctx.message.created_at
                )
                qumbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
                return await ctx.send(embed=qumbed)
            return await ctx.invoke(self.nowplaying)
        await ctx.send("I'm not in a voice channel")

    # NowPlaying
    @commands.command(name="nowplaying", aliases=["np"], help="Tells the playing music")
    @commands.guild_only()
    async def nowplaying(self, ctx:commands.Context):
        if ctx.voice_client:
            if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
                npmbed = discord.Embed(
                    color=self.color,
                    url=ctx.voice_client.current.uri,
                    title=F"Playing:\n{ctx.voice_client.current.title}",
                    description=F"By: {ctx.voice_client.current.author}\nRequested by {ctx.voice_client.current.requester.mention}\nDuration: {'%d:%d:%d'%((ctx.voice_client.current.length/(1000*60*60))%24, (ctx.voice_client.current.length/(1000*60))%60, (ctx.voice_client.current.length/1000)%60)}",
                    timestamp=ctx.voice_client.current.ctx.message.created_at
                )
                npmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
                return await ctx.send(embed=npmbed, view=ViewMusic(ctx, self))
            return await ctx.send("Nothing is playing")
        await ctx.send("I'm not in a voice channel")

    # Lyrics
    @commands.command(name="lyrics", aliases=["ly"], help="Shows the lyrics for music")
    @commands.guild_only()
    async def lyrics(self, ctx:commands.Context, *, music:str=None):
        if not music:
            if ctx.voice_client: music = F"{ctx.voice_client.current.title} {ctx.voice_client.current.author}"
            else: return await ctx.send("Since I'm not in a voice channel\nYou need to pass a music")
        lyrics = await self.bot.openrobot.lyrics(music)
        lymbed = discord.Embed(
            color=self.color,
            title=lyrics.title,
            description=self.bot.trim(lyrics.lyrics, 4096),
            timestamp=ctx.message.created_at
        )
        lymbed.set_thumbnail(url=lyrics.images.track or discord.Embed.Empty)
        lymbed.set_author(name=lyrics.artist, icon_url=lyrics.images.background or discord.Embed.Empty)
        lymbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=lymbed)

    @commands.Cog.listener()
    async def on_pomice_track_start(self, player:pomice.Player, track:pomice.Track):
        tsmbed = discord.Embed(
            color=self.color,
            url=track.uri,
            title=F"Playing:\n{track.title}",
            description=F"By: {track.author}\nRequested by {track.requester.mention}\nDuration: {'%d:%d:%d'%((track.length/(1000*60*60))%24, (track.length/(1000*60))%60, (track.length/1000)%60)}",
            timestamp=track.ctx.message.created_at
        )
        tsmbed.set_footer(text=track.requester, icon_url=track.requester.display_avatar.url)
        await track.ctx.send(embed=tsmbed, view=ViewMusic(track.ctx, self))

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player:pomice.Player, track:pomice.Track, reason:str):
        if not player.queue.empty():
            player.lqueue.pop(0)
            return await player.play(track=(await player.queue.get()))
        tembed = discord.Embed(
            color=self.color,
            url=track.uri,
            title=F"Ended:\n{track.title}",
            description=F"By: {track.author}\nRequested by {track.requester.mention}\nDuration: {'%d:%d:%d'%((track.length/(1000*60*60))%24, (track.length/(1000*60))%60, (track.length/1000)%60)}",
            timestamp=track.ctx.message.created_at
        )
        tembed.set_footer(text=track.requester, icon_url=track.requester.display_avatar.url)
        return await track.ctx.send(embed=tembed)
       

def setup(bot):
    bot.add_cog(Music(bot))
