import discord
from discord.ext import commands
from core.views import confirm

class Settings(commands.Cog, description="Setting up the bot with these!"):
    def __init__(self, bot):
        self.bot = bot

    # Prefix
    @commands.group(name="prefix", aliases=["pf"], help="Setting up the prefix with these, Consider using subcommands", invoke_without_command=True)
    @commands.guild_only()
    async def prefix(self, ctx:commands.Context):
        await ctx.send_help("prefix")

    # Prefix-Status
    @prefix.command(name="status", aliases=["st"], help="Shows the status for prefix")
    @commands.guild_only()
    async def prefix_status(self, ctx:commands.Context):
        pfstmbed = discord.Embed(
            color=self.bot.color,
            title=F"My Prefix here is:",
            description=self.bot.prefixes.get(ctx.guild.id),
            timestamp=ctx.message.created_at
        )
        pfstmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=pfstmbed)

    # Prefix-Change
    @prefix.command(name="change", aliases=["ch"], help="Changes the prefix to the new given text")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def prefix_change(self, ctx:commands.Context, *, text:str):
        prefix = await self.bot.postgres.fetchval("SELECT prefix FROM prefixes WHERE guild_id=$1", ctx.guild.id)
        pfchmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        pfchmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if text == prefix:
            pfchmbed.title = "Prefix is the same"
            pfchmbed.description = prefix
            return await ctx.reply(embed=pfchmbed)
        if not prefix:
            await self.bot.postgres.execute("INSERT INTO prefixes(guild_name,guild_id,prefix) VALUES ($1,$2,$3)", ctx.guild.name, ctx.guild.id, text)
        else:
            await self.bot.postgres.execute("UPDATE prefixes SET prefix=$1 WHERE guild_id=$2", text, ctx.guild.id)
        self.bot.prefixes[ctx.guild.id] = text
        pfchmbed.title = "Changed prefix:"
        pfchmbed.description = text
        await ctx.reply(embed=pfchmbed)

    # Prefix-Reset
    @prefix.command(name="reset", aliases=["rs"], help="Resets the prefix")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def prefix_reset(self, ctx:commands.Context):
        prefix = await self.bot.postgres.fetchval("SELECT prefix FROM prefixes WHERE guild_id=$1", ctx.guild.id)
        pfrsmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        pfrsmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if prefix:
            await self.bot.postgres.execute("DELETE FROM prefixes WHERE guild_id=$1", ctx.guild.id)
            pfrsmbed.title = "Resetted to:"
            pfrsmbed.description = self.bot.prefixes[ctx.guild.id] = self.bot.default_prefix
            return await ctx.reply(embed=pfrsmbed)
        pfrsmbed.title = "Prefix was never changed"
        pfrsmbed.description = self.bot.prefixes[ctx.guild.id]
        await ctx.reply(embed=pfrsmbed)

    # Welcome
    @commands.group(name="welcome", aliases=["wel"], help="Setting up the welcomer with these, Consider using subcommands", invoke_without_command=True)
    @commands.guild_only()
    async def welcome(self, ctx:commands.Context):
        await ctx.send_help("welcome")

    # Welcome-Status
    @welcome.command(name="status", aliases=["st"], help="Shows the status for welcome")
    @commands.guild_only()
    async def welcome_status(self, ctx:commands.Context):
        welcome = await self.bot.postgres.fetchval("SELECT * FROM welcome WHERE guild_id=$1", ctx.guild.id)
        welstmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        welstmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not welcome:
            welstmbed.title = "Welcome is turned off"
        else:
            msg = await self.bot.postgres.fetchval("SELECT msg FROM welcome WHERE guild_id=$1", ctx.guild.id)
            ch = discord.utils.get(ctx.guild.text_channels, id=(await self.bot.postgres.fetchval("SELECT ch FROM welcome WHERE guild_id=$1", ctx.guild.id)))
            welstmbed.title = "Status for welcome"
            welstmbed.description = F"Turned On\n{msg}\n{ch.mention}"
        await ctx.reply(embed=welstmbed)

    # Welcome-Toggle
    @welcome.command(name="toggle", aliases=["tg"], help="Toggles off or on the welcome")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def welcome_toggle(self, ctx:commands.Context):
        welcome = await self.bot.postgres.fetchval("SELECT * FROM welcome WHERE guild_id=$1", ctx.guild.id)
        welchmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        welchmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not welcome:
            await self.bot.postgres.execute("INSERT INTO welcome(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, "Welcome to .guild .member", ctx.guild.system_channel.id)
            welchmbed.title = "Welcome has been turned on"
        else:
            await self.bot.postgres.execute("DELETE FROM welcome WHERE guild_id=$1", ctx.guild.id)
            welchmbed.title = "Welcome has been turned off"
        await ctx.reply(embed=welchmbed)

    # Welcome-Channel
    @welcome.command(name="channel", aliases=["ch"], help="Changes the welcome channel to the new given channel")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def welcome_channel(self, ctx:commands.Context, channel:discord.TextChannel):
        welcome = await self.bot.postgres.fetchval("SELECT * FROM welcome WHERE guild_id=$1", ctx.guild.id)
        byechmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        byechmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not welcome:
            await self.bot.postgres.execute("INSERT INTO welcome(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, "Thank you .member for being here .guild", channel.id)
            byechmbed.title = "Welcome channel has been changed to:"
            byechmbed.description = channel.mention
        else:
            await self.bot.postgres.execute("UPDATE welcome SET ch=$1 WHERE guild_id=$2", channel.id, ctx.guild.id)
            byechmbed.title = "Welcome channel has been changed to:"
            byechmbed.description = channel.mention
        await ctx.reply(embed=byechmbed)

    # Welcome-Message
    @welcome.command(name="message", aliases=["msg"], help="Changes the welcome message to the new given message")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def welcome_message(self, ctx:commands.Context, *, msg:str):
        welcome = await self.bot.postgres.fetchval("SELECT * FROM welcome WHERE guild_id=$1", ctx.guild.id)
        welmsgmbed = discord.Embed(
            color=self.bot.color,
            title="Welcome message has been changed to:",
            description=msg,
            timestamp=ctx.message.created_at
        )
        welmsgmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not welcome:
            await self.bot.postgres.execute("INSERT INTO welcome(guild_name,guild_id,msg) VALUES($1,$2,$3)", ctx.guild.name, ctx.guild.id, msg)
        else:
            await self.bot.postgres.execute("UPDATE welcome SET msg=$1 WHERE guild_id=$2", msg, ctx.guild.id)
        await ctx.reply(embed=welmsgmbed)

    # Goodbye
    @commands.group(name="goodbye", aliases=["bye"], help="Setting up the goodbyer with these, Consider using subcommands", invoke_without_command=True)
    @commands.guild_only()
    async def goodbye(self, ctx:commands.Context):
        await ctx.send_help("goodbye")

    # Goodbye-Status
    @goodbye.command(name="status", aliases=["st"], help="Changes the status for goodbye")
    @commands.guild_only()
    async def goodbye_status(self, ctx:commands.Context):
        goodbye = await self.bot.postgres.fetchval("SELECT * FROM goodbye WHERE guild_id=$1", ctx.guild.id)
        byestmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        byestmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not goodbye:
            byestmbed.title = "Goodbye is turned off"
        else:
            msg = await self.bot.postgres.fetchval("SELECT msg FROM goodbye WHERE guild_id=$1", ctx.guild.id)
            ch = discord.utils.get(ctx.guild.text_channels, id=(await self.bot.postgres.fetchval("SELECT ch FROM goodbye WHERE guild_id=$1", ctx.guild.id)))
            byestmbed.title = "Status for goodbye"
            byestmbed.description = F"Turned On\n{msg}\n{ch.mention}"
        await ctx.reply(embed=byestmbed)

    # Goodbye-Toggle
    @goodbye.command(name="toggle", aliases=["tg"], help="Toggles off or on the goodbye")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def goodbye_toggle(self, ctx:commands.Context):
        goodbye = await self.bot.postgres.fetchval("SELECT * FROM goodbye WHERE guild_id=$1", ctx.guild.id)
        byechmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        byechmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not goodbye:
            await self.bot.postgres.execute("INSERT INTO goodbye(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, "Thank you .member for being here .guild", ctx.guild.system_channel.id)
            byechmbed.title = "Goodbye has been turned on"
        else:
            await self.bot.postgres.execute("DELETE FROM goodbye WHERE guild_id=$1", ctx.guild.id)
            byechmbed.title = "Goodbye has been turned off"
        await ctx.reply(embed=byechmbed)

    # Goodbye-Channel
    @goodbye.command(name="channel", aliases=["ch"], help="Changes the goodbye channel to the new given channel")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def goodbye_channel(self, ctx:commands.Context, channel:discord.TextChannel):
        goodbye = await self.bot.postgres.fetchval("SELECT * FROM goodbye WHERE guild_id=$1", ctx.guild.id)
        byechmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        byechmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not goodbye:
            await self.bot.postgres.execute("INSERT INTO goodbye(guild_name,guild_id,msg,ch) VALUES($1,$2,$3,$4)", ctx.guild.name, ctx.guild.id, "Thank you .member for being here .guild", channel.id)
            byechmbed.title = "Goodbye channel has been changed to:"
            byechmbed.description = channel.mention
        else:
            await self.bot.postgres.execute("UPDATE goodbye SET ch=$1 WHERE guild_id=$2", channel.id, ctx.guild.id)
            byechmbed.title = "Goodbye channel has been changed to:"
            byechmbed.description = channel.mention
        await ctx.reply(embed=byechmbed)

    # Goodbye-Message
    @goodbye.command(name="message", aliases=["msg"], help="Changes the goodbye message to the new given message")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def goodbye_message(self, ctx:commands.Context, *, msg:str):
        goodbye = await self.bot.postgres.fetchval("SELECT * FROM goodbye WHERE guild_id=$1", ctx.guild.id)
        byemsgmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        byemsgmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not goodbye:
            await self.bot.postgres.execute("INSERT INTO goodbye(guild_name,guild_id,msg) VALUES($1,$2,$3)", ctx.guild.name, ctx.guild.id, msg)
            byemsgmbed.title = "Goodbye message has been changed to:"
            byemsgmbed.description = msg
        else:
            await self.bot.postgres.execute("UPDATE goodbye SET msg=$1 WHERE guild_id=$2", msg, ctx.guild.id)
            byemsgmbed.title = "Goodbye message has been changed to:"
            byemsgmbed.description = msg
        await ctx.reply(embed=byemsgmbed)

    # Leave
    @commands.command(name="leave", aliases=["lae"], help="Makes the bot leave")
    @commands.has_guild_permissions(administrator=True)
    async def leave(self, ctx:commands.Context):
        laembed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        laembed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        view = confirm.ViewConfirm(ctx)
        view.message = await ctx.reply(content="Are you sure you want the bot to leave:", view=view)
        await view.wait()
        if view.value:
            laembed.title = F"{self.bot.user} has left"
            await ctx.reply(embed=laembed, delete_after=2.5)
            await ctx.me.guild.leave()

def setup(bot):
    bot.add_cog(Settings(bot))