import discord, pomice, io, textwrap, contextlib, traceback
from discord.ext import commands
from core.views import confirm
class Owner(commands.Cog, description="Only my Developer can use these!"):
    def __init__(self, bot):
        self.bot = bot

    # Eval
    @commands.command(name="eval", help="Evaluates the given code")
    @commands.is_owner()
    async def _eval(self, ctx, *, body:str):
        dad = await self.bot.fetch_user(494496285676535811)
        env = {
            "self": self,
            "discord": discord,
            "commands": commands,
            "player": pomice.Player,
            "track": pomice.Track,
            "bot": self.bot,
            "dad": dad,
            "ctx": ctx,
            "message": ctx.message,
            "author": ctx.author,
            "guild": ctx.guild,
            "channel": ctx.channel,
        }
        env.update(globals())
        if body.startswith("```") and body.endswith("```"):
            body = "\n".join(body.split("\n")[1:-1])
        body = body.strip("` \n")
        stdout = io.StringIO()
        to_compile = F"async def func():\n{textwrap.indent(body, '  ')}"
        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.reply(f"```py\n{e.__class__.__name__}: {e}\n```")
        func = env["func"]
        try:
            with contextlib.redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.reply(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction("\u2705")
            except:
                pass
            if ret is None:
                if value:
                    await ctx.reply(f"```py\n{value}\n```")
            else:
                await ctx.reply(f"```py\n{value}{ret}\n```")

    # Load
    @commands.command(name="load", help="Loads the given cog")
    @commands.is_owner()
    async def load(self, ctx:commands.Context, *, cog:str):
        loadmbed = discord.Embed(
            color=self.bot.color,
            title=F"Loaded {cog}.",
            timestamp=ctx.message.created_at
        )
        loadmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        self.bot.load_extension(cog)
        await ctx.reply(embed=loadmbed)

    # Unload
    @commands.command(name="unload", help="Unloads the given cog")
    @commands.is_owner()
    async def unload(self, ctx:commands.Context, *, cog:str):
        unloadmbed = discord.Embed(
            color=self.bot.color,
            title=F"Unloaded {cog}.",
            timestamp=ctx.message.created_at
        )
        unloadmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        self.bot.unload_extension(cog)
        await ctx.reply(embed=unloadmbed)
  
    # Reload
    @commands.command(name="reload", help="Reloads the given or every cog")
    @commands.is_owner()
    async def reload(self, ctx:commands.Context, *, cog:str=None):
        reloadmbed = discord.Embed(
            color=self.bot.color,
            description="",
            timestamp=ctx.message.created_at
        )
        if not cog:
            reloadmbed.title = "Reloaded every cog"
            reloadmbed.description += F"Commands:\n"
            for command in self.bot._commands:
                try:
                    self.bot.reload_extension(F"core.commands.{command}")
                    reloadmbed.description += F"<:xof:913092545746174042> <:yon:913093094348558356> {command}\n"
                except Exception as error:
                    reloadmbed.description += F"<:xon:913093019866136636> <:yof:913092780308447235> {command}\n"
                    reloadmbed.description += F"<:xon:913093019866136636> <:yof:913092780308447235> {error}\n"
            reloadmbed.description += F"Events:\n"
            for event in self.bot._events:
                try:
                    self.bot.reload_extension(F"core.events.{event}")
                    reloadmbed.description += F"<:xof:913092545746174042> <:yon:913093094348558356> {event}\n"
                except Exception as error:
                    reloadmbed.description += F"<:xon:913093019866136636> <:yof:913092780308447235> {event}\n"
                    reloadmbed.description += F"<:xon:913093019866136636> <:yof:913092780308447235> {error}\n"
            return await ctx.reply(embed=reloadmbed)
        reloadmbed.title = F"Reloaded {cog}."
        self.bot.reload_extension(cog)
        await ctx.reply(embed=reloadmbed)

    # Toggle
    @commands.command(name="toggle", help="Toggles on and off the given command")
    @commands.is_owner()
    async def toggle(self, ctx:commands.Context, command:str):
        command = self.bot.get_command(command)
        if not command.enabled:
            command.enabled = True
            await ctx.reply(F"Enabled {command.name} command")
        else:
            command.enabled = False
            await ctx.reply(F"Disabled {command.name} command.")

    # Repeat
    @commands.command(name="repeat", help="Repeats the given commands the amounts of given time")
    @commands.is_owner()
    async def repeat(self, ctx:commands.Context, time:int, command:str):
        for _ in range(1, time+1):
            await self.bot.process_commands(command)
        await ctx.reply(F"Repeated `{command}` - `{time}` times")

    # Leaves
    @commands.command(name="lives", help="Leaves from the given guilds")
    @commands.is_owner()
    async def lives(self, ctx:commands.Context, *, guild:int):
        g = await self.bot.fetch_guild(guild)
        livesmbed = discord.Embed(
            color=self.bot.color,
            title="Living the given guilds:",
            description=F"{g.name} {g.id} {'No Owner' if not g.owner else g.owner}",
            timestamp=ctx.message.created_at
        )
        view = confirm.ViewConfirm(ctx)
        view.message = await ctx.reply(content="Are you sure you want the bot to live the given guild?", embed=livesmbed, view=view)
        await view.wait()
        if view.value:
            await g.leave()

    # Shutdown
    @commands.command(name="shutdown",  help="Shutdowns the bot")
    @commands.is_owner()
    async def logout(self, ctx:commands.Context):
        shutdownmbed = discord.Embed(
            color=self.bot.color,
            title="I'm shutting-down",
            timestamp=ctx.message.created_at
        )
        shutdownmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=shutdownmbed)
        await self.bot.close()

    # Blacklist
    @commands.command(name="blacklist", help="Puts-in or Puts-out the given user from blacklist")
    @commands.is_owner()
    async def blacklist(self, ctx:commands.Context, user:discord.User=None, *, reason:str=None):
        reason = "Nothing was provided" if not reason else reason
        if not user:
            blacklistsmbed = discord.Embed(
                color=self.bot.color,
                description="",
                timestamp=ctx.message.created_at
            )
            blacklistsmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
            blacklisted = await self.bot.postgres.fetch("SELECT * FROM blacklist")
            if not blacklisted:
                blacklistsmbed.title += "Nobody is in Blacklist"
            else:
                blacklistsmbed.title = "Users in Blacklist"
                for users in blacklisted:
                    user = self.bot.get_user(users["user_id"])
                    blacklistsmbed.description += F"{user} | {user.mention} - {users['reason']}\n"
            return await ctx.reply(embed=blacklistsmbed)
        blacklisted = await self.bot.postgres.fetchval("SELECT user_id FROM blacklist WHERE user_id=$1", user.id)
        blacklistmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        blacklistmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not blacklisted:
            await self.bot.postgres.execute("INSERT INTO blacklist(user_name,user_id,reason) VALUES($1,$2,$3)", user.name, user.id, reason)
            blacklistmbed.title = F"Added {user} to blacklist"
        else:
            await self.bot.postgres.execute("DELETE FROM blacklist WHERE user_id=$1", user.id)
            blacklistmbed.title = F"Removed {user} from blacklist"
        await ctx.reply(embed=blacklistmbed)

    # Screenshot
    @commands.command(name="screenshot", aliases=["ss"], help="Gives a preview from the given website")
    @commands.is_owner()
    @commands.bot_has_guild_permissions(attach_files=True)
    async def screenshot(self, ctx:commands.Context, *, website:str):
        session = await self.bot.session.get(F"https://api.screenshotmachine.com?key=a95edd&url={website}&dimension=1024x768")
        response = io.BytesIO(await session.read())
        ssmbed = discord.Embed(
            color=self.bot.color,
            title="Here is your screenshot",
            timestamp=ctx.message.created_at
        )
        ssmbed.set_image(url="attachment://screenshot.png")
        ssmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(file=discord.File(fp=response, filename="screenshot.png"), embed=ssmbed)

def setup(bot):
    bot.add_cog(Owner(bot))