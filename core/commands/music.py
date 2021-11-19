import discord, pomice, re, asyncio, datetime
from discord.ext import commands
from core.views import confirm, pagination

URL_REG = re.compile(r"https?://(?:www\.)?.+")

class ViewPlayer(discord.ui.View):
    def __init__(self, ctx, music):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.music = music

    @discord.ui.button(emoji="⏯", style=discord.ButtonStyle.green)
    async def ue(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            if self.ctx.voice_client.is_paused:
                await interaction.response.send_message(F"Resumed: {self.ctx.voice_client.current.title} | {self.ctx.voice_client.current.author}", ephemeral=True)
                return await self.ctx.voice_client.set_pause(pause=False)
            await interaction.response.send_message(F"Paused: {self.ctx.voice_client.current.title} - {self.ctx.voice_client.current.author}", ephemeral=True)
            return await self.ctx.voice_client.set_pause(pause=True)
        return await interaction.response.send_message("Resume/Pause: Nothing is playing", ephemeral=True)

    @discord.ui.button(emoji="⏹", style=discord.ButtonStyle.red)
    async def stop(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            if not self.ctx.voice_client.queue.empty():
                for _ in range(self.ctx.voice_client.queue.qsize()):
                    self.ctx.voice_client.queue.get_nowait()
                    self.ctx.voice_client.queue.task_done()
                for _ in range(len(self.ctx.voice_client.lqueue)):
                    self.ctx.voice_client.lqueue.pop(0)
            await interaction.response.send_message(F"Stopped: {self.ctx.voice_client.current.title} | {self.ctx.voice_client.current.author}", ephemeral=True)
            return await self.ctx.voice_client.stop()
        return await interaction.response.send_message("Stop: Nothing is playing", ephemeral=True)

    @discord.ui.button(emoji="⏺", style=discord.ButtonStyle.red)
    async def destroy(self, button:discord.ui.Button, interaction:discord.Interaction):
        if not self.ctx.voice_client.queue.empty():
            for _ in range(self.ctx.voice_client.queue.qsize()):
                self.ctx.voice_client.queue.get_nowait()
                self.ctx.voice_client.queue.task_done()
            for _ in range(len(self.ctx.voice_client.lqueue)):
                self.ctx.voice_client.lqueue.pop(0)
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            await interaction.response.send_message(F"Destroyed: {self.ctx.voice_client.current.title} | {self.ctx.voice_client.current.author}", ephemeral=True)
        else:
            await interaction.response.send_message("Destroyed", ephemeral=True)
        return await self.ctx.voice_client.destroy()

    @discord.ui.button(emoji="⏭", style=discord.ButtonStyle.blurple)
    async def skip(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            if not self.ctx.voice_client.queue.empty():
                await interaction.response.send_message(F"Skipped: {self.ctx.voice_client.current.title} | {self.ctx.voice_client.current.author}", ephemeral=True)
                return await self.ctx.voice_client.stop()
            return await interaction.response.send_message("Skip: There is nothing in the queue", ephemeral=True)
        return await interaction.response.send_message("Skip: Nothing is playing", ephemeral=True)

    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.blurple)
    async def loop(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            if not self.ctx.voice_client.loop:
                self.ctx.voice_client.loop = self.ctx.voice_client.current
                return await interaction.response.send_message(F"Loop: turned on | {self.ctx.voice_client.current.title} - {self.ctx.voice_client.current.author}", ephemeral=True)
            self.ctx.voice_client.loop = None
            return await interaction.response.send_message(F"Loop: turned off | {self.ctx.voice_client.current.title} - {self.ctx.voice_client.current.author}", ephemeral=True)
        return await interaction.response.send_message.send("Loop: Nothing is playing", ephemeral=True)

    async def nowplaying(self, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            npmbed = discord.Embed(
                color=self.ctx.bot.music_color,
                title="Playing:",
                description=F"Title: [{self.ctx.voice_client.current.title}]({self.ctx.voice_client.current.uri})\nBy: {self.ctx.voice_client.current.author}\nRequester: {self.ctx.voice_client.current.requester.mention}\nDuration: {self.music.bar(self.ctx.voice_client.position, self.ctx.voice_client.current.length)} | {self.music.duration(self.ctx.voice_client.position)} - {self.music.duration(self.ctx.voice_client.current.length)}\n{f'Next: {self.ctx.voice_client.lqueue[1]}' if len(self.ctx.voice_client.lqueue) > 1 else ''}",
                timestamp=self.ctx.voice_client.current.ctx.message.created_at
            )
            npmbed.set_thumbnail(url=self.ctx.voice_client.current.thumbnail or discord.Embed.Empty)
            npmbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=npmbed, ephemeral=True)
        return await interaction.response.send_message.send("Queue: Nothing is playing", ephemeral=True)

    @discord.ui.button(emoji="🎦", style=discord.ButtonStyle.grey)
    async def queue(self, button:discord.ui.Button, interaction:discord.Interaction):
        if len(self.ctx.voice_client.lqueue) > 1:
            d = "\n".join(q for q in self.ctx.voice_client.lqueue)
            qumbed = discord.Embed(
                color=self.ctx.bot.music_color,
                title="Queue",
                description=self.ctx.bot.trim(d, 4095),
                timestamp=self.ctx.message.created_at
            )
            qumbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
            return await interaction.response.send_message(embed=qumbed, ephemeral=True)
        return await self.nowplaying()

    @discord.ui.button(emoji="🔢", style=discord.ButtonStyle.grey)
    async def lyrics(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.ctx.voice_client.is_playing or self.ctx.voice_client.is_paused:
            lyrics = await self.ctx.bot.openrobot.lyrics(self.ctx.voice_client.current.title)
            if lyrics.lyrics:
                lymbed = discord.Embed(
                    color=self.ctx.bot.music_color,
                    title=lyrics.title,
                    description=lyrics.lyrics[:4096],
                    timestamp=self.ctx.message.created_at
                )
                lymbed.set_thumbnail(url=lyrics.images.track or discord.Embed.Empty)
                lymbed.set_author(name=lyrics.artist, icon_url=lyrics.images.background or discord.Embed.Empty)
                lymbed.set_footer(text=interaction.user, icon_url=interaction.user.display_avatar.url)
                return await interaction.response.send_message(embed=lymbed, ephemeral=True)
            return await interaction.response.send_message(F"Lyrics: Didn't find any, {self.ctx.voice_client.current.title} - {self.ctx.voice_client.current.author}", ephemeral=True)
        return await interaction.response.send_message.send("Lyrics: Nothing is playing", ephemeral=True)

    async def interaction_check(self, interaction:discord.Interaction):
        if self.ctx.voice_client:
            if interaction.user.voice:
                for member in self.ctx.me.voice.channel.members:
                    if interaction.user.id == member.id: return True
                await interaction.response.send_message(F"Only the people in {self.ctx.me.voice.channel.mention} can use this", ephemeral=True)
                return False
            await interaction.response.send_message("You must be in voice channel", ephemeral=True)
            return False
        await interaction.response.send_message("I'm not in a voice channel", ephemeral=True)
        return False

class Music(commands.Cog, description="Jamming out with these!"):
    def __init__(self, bot):
        self.bot = bot

    def duration(self, length):
        return '%d:%d:%d'%((length/(1000*60*60))%24, (length/(1000*60))%60, (length/1000)%60)

    def bar(self, position, length, size=10):
        done = int((position/length)*size)
        return F"{'🔷'*done}{'🔶'*(size-done)}"

    def bot_voice(ctx:commands.Context):
        if ctx.voice_client:
            return True
        raise commands.CheckFailure("I'm not in a voice channel")

    def user_voice(ctx:commands.Context):
        if ctx.author.voice:
            return True
        raise commands.CheckFailure("You must be in voice channel")

    def full_voice(ctx:commands.Context):
        if ctx.me.voice:
            if ctx.author.voice:
                if ctx.me.voice.channel == ctx.author.voice.channel:
                    return True
                raise commands.CheckFailure(F"You must be in the same voice channel, {ctx.me.voice.channel.mention}")
            raise commands.CheckFailure("You must be in voice channel")
        raise commands.CheckFailure("I'm not in a voice channel")

    # Player
    @commands.command(name="player", alieses=["pr"], help="Shows you the ultimate player")
    @commands.guild_only()
    @commands.check(full_voice)
    async def player(self, ctx:commands.Context):
        if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            return await ctx.reply("Pemgu.Player.exe", view=ViewPlayer(ctx, self))
        return await ctx.reply("Nothing is playing")

    # Join
    @commands.command(name="join", aliases=["jn"], help="Joins a voice channel")
    @commands.guild_only()
    @commands.check(user_voice)
    async def join(self, ctx:commands.Context, channel:discord.VoiceChannel=None):
        channel = ctx.author.voice.channel if not channel else channel
        if not ctx.me.voice:
            if channel.permissions_for(ctx.me).connect:
                await ctx.author.voice.channel.connect(cls=pomice.Player)
                await ctx.guild.change_voice_state(channel=channel, self_deaf=True)
                ctx.voice_client.queue = asyncio.Queue()
                ctx.voice_client.lqueue = []
                ctx.voice_client.loop = None
                return await ctx.reply(F"Joined the voice channel {ctx.author.voice.channel.mention}")
            return await ctx.reply("I don't have permission to join that channel")
        await ctx.reply(F"Someone else is using to me in {ctx.me.voice.channel.mention}")

    # Disconnect
    @commands.command(name="disconnect", aliases=["dc"], help="Disconnects from the voice channel")
    @commands.guild_only()
    @commands.check(full_voice)
    async def disconnect(self, ctx:commands.Context):
        await ctx.voice_client.destroy()                    
        return await ctx.reply("Disconnected from the voice channel")

    # Play
    @commands.command(name="play", aliases=["pl"], help="Plays music with the given term, term can be a url or a query or a playlist")
    @commands.guild_only()
    @commands.check(user_voice)
    async def play(self, ctx:commands.Context, *, term:str):
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        if not ctx.author.voice:
            return await ctx.reply("You must be in a voice channel")
        if ctx.me.voice.channel == ctx.author.voice.channel:
            results = await ctx.voice_client.get_tracks(query=term, ctx=ctx)
            print(results)
            if not results:
                return await ctx.reply("No results were found for that search term.")
            if isinstance(results, pomice.Playlist):
                for track in results.tracks:
                    await ctx.voice_client.queue.put(track)
                    ctx.voice_client.lqueue.append(F"{track.title} - {track.author} | {ctx.author.mention}")
            elif isinstance(results, pomice.Track):
                await ctx.voice_client.queue.put(results.title)
                ctx.voice_client.lqueue.append(F"{results.title} - {results.author} | {ctx.author.mention}")
            else:
                await ctx.voice_client.queue.put(results[0])
                ctx.voice_client.lqueue.append(F"{results[0].title} - {results[0].author} | {ctx.author.mention}")
            if not ctx.voice_client.is_playing:
                return await ctx.voice_client.play(track=(await ctx.voice_client.queue.get()))
            return await ctx.reply(F"Added {results if isinstance(results, pomice.Playlist) else results[0]} to the queue")
        return await ctx.reply(F"Someone else is using to me in {ctx.me.voice.channel.mention}")

    # Stop
    @commands.command(name="stop", aliases=["so"], help="Stops playing and Clears queue")
    @commands.guild_only()
    @commands.check(full_voice)
    async def stop(self, ctx:commands.Context):
        if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            for _ in range(ctx.voice_client.queue.qsize()):
                    ctx.voice_client.queue.get_nowait()
                    ctx.voice_client.queue.task_done()
            for _ in range(len(ctx.voice_client.lqueue)):
                ctx.voice_client.lqueue.pop(0)
            await ctx.reply(F"Stopped: {ctx.voice_client.current.title} - {ctx.voice_client.current.author}")
            return await ctx.voice_client.stop()
        return await ctx.reply("Nothing is playing")

    # Skip
    @commands.command(name="skip", aliases=["sk"], help="Skips the music")
    @commands.guild_only()
    @commands.check(full_voice)
    async def skip(self, ctx:commands.Context):
        if ctx.voice_client.is_playing:
            if not ctx.voice_client.queue.empty():
                await ctx.reply(F"Skipped: {ctx.voice_client.current.title} | {ctx.voice_client.current.author}")
                return await ctx.voice_client.stop()
            return await ctx.reply("There is nothing in the queue")
        return await ctx.reply("Nothing is playing")

    # Resume
    @commands.command(name="resume", aliases=["ru"], help="Resumes the paused music")
    @commands.guild_only()
    @commands.check(full_voice)
    async def resume(self, ctx:commands.Context):
        if ctx.voice_client.is_paused:
            await ctx.voice_client.set_pause(pause=False)
            return await ctx.reply("Resumed the music")
        return await ctx.reply("The music is already playing")

    # Pause
    @commands.command(name="pause", aliases=["pu"], help="Pauses playing music")
    @commands.guild_only()
    @commands.check(full_voice)
    async def pause(self, ctx:commands.Context):
        if ctx.voice_client.is_playing:
            await ctx.voice_client.set_pause(pause=True)
            return await ctx.reply("Paused the music")
        return await ctx.reply("Music is already paused")

    # Loop
    @commands.command(name="loop", aliases=["lp"], help="Loops over the music")
    @commands.guild_only()
    @commands.check(full_voice)
    async def loop(self, ctx:commands.Context):
        if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            if not ctx.voice_client.loop:
                ctx.voice_client.loop = ctx.voice_client.current
                return await ctx.reply(F"Loop has been turned on - {ctx.voice_client.current.title} - {ctx.voice_client.current.author}")
            ctx.voice_client.loop = None
            return await ctx.reply(F"Loop has been turned off - {ctx.voice_client.current.title} - {ctx.voice_client.current.author}")
        return await ctx.reply("Nothing is playing")

    # NowPlaying
    @commands.command(name="nowplaying", aliases=["np"], help="Tells the playing music")
    @commands.guild_only()
    @commands.check(bot_voice)
    async def nowplaying(self, ctx:commands.Context):
        if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            npmbed = discord.Embed(
                color=self.bot.music_color,
                title="Playing:",
                description=F"Title: [{ctx.voice_client.current.title}]({ctx.voice_client.current.uri})\nBy: {ctx.voice_client.current.author}\nRequester: {ctx.voice_client.current.requester.mention}\nDuration: {self.bar(ctx.voice_client.position, ctx.voice_client.current.length)} | {self.duration(ctx.voice_client.position)} - {self.duration(ctx.voice_client.current.length)}\n{f'Next: {ctx.voice_client.lqueue[1]}' if len(ctx.voice_client.lqueue) > 1 else ''}",
                timestamp=ctx.voice_client.current.ctx.message.created_at
            )
            npmbed.set_thumbnail(url=ctx.voice_client.current.thumbnail or discord.Embed.Empty)
            npmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
            return await ctx.reply(embed=npmbed)
        return await ctx.reply("Nothing is playing")

    # Queue
    @commands.command(name="queue", aliases=["qu"], help="Shows the queue")
    @commands.guild_only()
    @commands.check(bot_voice)
    async def queue(self, ctx:commands.Context):
        if len(ctx.voice_client.lqueue) > 1:
            es = []
            paginator = commands.Paginator()
            for i in ctx.voice_client.lqueue:
                paginator.add_line(str(i))
            for page in paginator.pages:
                qumbed = discord.Embed(
                    color=self.bot.music_color,
                    title="Queue",
                    description=page,
                    timestamp=ctx.message.created_at
                )
                qumbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
                es.append(qumbed)
            return await ctx.reply(embed=es[0], view=pagination.ViewPagination(ctx, es))
        return await ctx.invoke(self.nowplaying)

    # Queue-Clear
    @commands.command(name="queueclear", aliases=["qucr"], help="Clears the queue")
    @commands.guild_only()
    @commands.check(full_voice)
    async def queue_clear(self, ctx:commands.Context):
        if not ctx.voice_client.queue.empty():
            await ctx.invoke(self.queue)
            view = confirm.Confirm(ctx)
            await ctx.reply("Do you want to clear the queue", view=view)
            await view.wait()
            if view.value:
                for _ in range(ctx.voice_client.queue.qsize()):
                    ctx.voice_client.queue.get_nowait()
                    ctx.voice_client.queue.task_done()
                for _ in range(len(ctx.voice_client.lqueue)):
                    ctx.voice_client.lqueue.pop(0)
                return await ctx.reply("Queue has been cleared")
            return await ctx.reply("Queue has not been cleared")
        return await ctx.reply("Nothing is in the queue")

    # Seek
    @commands.command(name="seek", aliases=["se"], help="Seeks to the given time")
    @commands.guild_only()
    @commands.check(full_voice)
    async def seek(self, ctx:commands.Context, *, time:str=None):
        if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            if ":" in time:
                time = time.split(":")
                dtime = datetime.timedelta(hours=int(time[0]), minutes=int(time[1]), seconds=int(time[2]))
                mtime = dtime.seconds*1000
                if not (mtime) >= ctx.voice_client.current.length:
                    sembed = discord.Embed(
                        color=self.bot.music_color,
                        description=F"Seeked: {self.duration(mtime)}\nTitle: [{ctx.voice_client.current.title}]({ctx.voice_client.current.uri})\nBy: {ctx.voice_client.current.author}\nRequester: {ctx.voice_client.current.requester.mention}\nDuration: {self.bar(mtime, ctx.voice_client.current.length)} | {self.duration(mtime)} - {self.duration(ctx.voice_client.current.length)}",
                        timestamp=ctx.message.created_at
                    )
                    sembed.set_thumbnail(url=ctx.voice_client.current.thumbnail or discord.Embed.Empty)
                    sembed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
                    await ctx.voice_client.seek(mtime)
                    return await ctx.reply(embed=sembed)
                return await ctx.reply(F"Time needs to be between 0 or {self.duration(ctx.voice_client.current.length)}")
            return await ctx.reply(F"Time need to be like 0:1:23")

    # Volume
    @commands.command(name="volume", aliases=["vol"], help="Sets or Tells the volume of the music")
    @commands.guild_only()
    @commands.check(full_voice)
    async def volume(self, ctx:commands.Context, *, volume:int=None):
        if ctx.voice_client.is_playing or ctx.voice_client.is_paused:
            if volume:
                if not volume < 0 or not volume > 500:
                    await ctx.voice_client.set_volume(volume)
                    return await ctx.reply(F"Volume has been changed to {volume}")
                return await ctx.reply("The volume must be between 0 and 500")
            return await ctx.reply(F"The volume is currently at {ctx.voice_client.volume}")
        return await ctx.reply("Nothing is playing")

    # Lyrics
    @commands.command(name="lyrics", aliases=["ly"], help="Shows the lyrics for music")
    @commands.guild_only()
    async def lyrics(self, ctx:commands.Context, *, music:str=None):
        if not music:
            if ctx.voice_client: music = ctx.voice_client.current.title
            else: raise commands.CheckFailure("Since I'm not in a voice channel you need to pass a music")
        lyrics = await self.bot.openrobot.lyrics(music)
        if lyrics.lyrics:
            lymbed = discord.Embed(
                color=self.bot.music_color,
                title=lyrics.title,
                description=lyrics.lyrics[:4096],
                timestamp=ctx.message.created_at
            )
            lymbed.set_thumbnail(url=lyrics.images.track or discord.Embed.Empty)
            lymbed.set_author(name=lyrics.artist, icon_url=lyrics.images.background or discord.Embed.Empty)
            return await ctx.reply(embed=lymbed)
        await ctx.reply(F"Didn't find any lyrics for {music}")

    @commands.Cog.listener()
    async def on_pomice_track_start(self, player:pomice.Player, track:pomice.Track):
        tsmbed = discord.Embed(
            color=self.bot.music_color,
            title="Playing:",
            description=F"Title: [{track.title}]({track.uri})\nBy: {track.author}\nRequester: {track.requester.mention}\nDuration: {self.bar(player.position, track.length)} | {self.duration(player.position)} - {self.duration(track.length)}\n{f'Next: {player.lqueue[1]}' if len(player.lqueue) > 1 else ''}",
            timestamp=track.ctx.message.created_at
        )
        tsmbed.set_thumbnail(url=track.thumbnail or discord.Embed.Empty)
        tsmbed.set_footer(text=track.requester, icon_url=track.requester.display_avatar.url)
        await track.ctx.reply(embed=tsmbed)

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player:pomice.Player, track:pomice.Track, reason:str):
        if not player.loop:
            if player.queue.empty():
                tembed = discord.Embed(
                    color=self.bot.music_color,
                    title="Ended:",
                    description=F"Title: [{track.title}]({track.uri})\nBy: {track.author}\nRequester: {track.requester.mention}\nDuration: {self.bar(track.length, track.length)} | {self.duration(track.length)} - {self.duration(track.length)}",
                    timestamp=track.ctx.message.created_at
                )
                tembed.set_thumbnail(url=track.thumbnail or discord.Embed.Empty)
                tembed.set_footer(text=track.requester, icon_url=track.requester.display_avatar.url)
                return await track.ctx.reply(embed=tembed)
            player.lqueue.pop(0)
            return await player.play(track=(await player.queue.get()))
        await player.play(track=player.loop)

def setup(bot):
    bot.add_cog(Music(bot))