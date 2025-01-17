import discord, expr, asyncio
from discord.ext import commands
from core.views import confirm

class Utility(commands.Cog, description="Useful stuff that are open to everyone"):
    def __init__(self, bot):
        self.bot = bot

    # Cleanup
    @commands.command(name="cleanup", aliases=["cu"], help="Deletes bot's messagess")
    async def cleanup(self, ctx:commands.Context, *, amount:int):
        cumbed = discord.Embed(
            color=self.bot.color,
            title=F"Cleaned-up {amount} of bot messages",
        )
        cumbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.channel.purge(limit=amount, check=lambda m: m.author.id == self.bot.user.id, bulk=False)
        await ctx.reply(embed=cumbed, delete_after=5)

    # Calculator
    @commands.command(name="calculator", aliases=["calc"], help="Calculates the given math")
    async def calculator(self, ctx:commands.Context, *, math:str):
        output = expr.evaluate(math)
        calcmbed = discord.Embed(
            color=self.bot.color,
            title="Here is your math:",
            description=F"Input: **{math}**\nOutput: **{output}**",
            timestamp=ctx.message.created_at
        )
        calcmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=calcmbed)

    # Remind
    @commands.command(name="remind", aliases=["rm"], help="Reminds you with the given task and seconds")
    async def remind(self, ctx:commands.Context, seconds:int, *, task:str):
        await ctx.reply(F"{ctx.author.mention}, in {seconds} seconds:, I will remind you About: **{task}**", allowed_mentions=discord.AllowedMentions(users=True))
        await asyncio.sleep(seconds)
        view = discord.ui.View()
        view.add_item(item=discord.ui.Button(label="Go to original message", url=ctx.message.jump_url))
        await ctx.reply(F"{ctx.author.mention} Reminded you, as you said in {seconds} seconds, it's been **{discord.utils.format_dt(ctx.message.created_at, style='R')}**, About: **{task}**", view=view, allowed_mentions=discord.AllowedMentions(users=True))

    # AFK
    @commands.command(name="afk", help="Makes you AFK")
    async def afk(self, ctx:commands.Context, *, reason:str=None):
        reason = "You didn't provide anything" if not reason else reason
        afk = self.bot.afks.get(ctx.author.id)
        afkmbed  = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        afkmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not afk:
            afk = self.bot.afks[ctx.author.id] = {"time":discord.utils.utcnow(), "reason":reason, "jump_url":ctx.message.jump_url}
            view = discord.ui.View()
            view.add_item(item=discord.ui.Button(label="Go to original message", url=afk["jump_url"]))
            afkmbed.title = "Set your AFK"
            afkmbed.description = F"Reason: **{afk['reason']}**"
            await ctx.reply(embed=afkmbed)

    # Notes
    @commands.group(name="notes", aliases=["note"], help="Taking notes with these, Consider using subcommands", invoke_without_command=True)
    async def notes(self, ctx:commands.Context):
        await ctx.send_help("notes")

    # Notes-List
    @notes.command(name="list", aliases=["lt"], help="Shows every of your or the given user's notes")
    async def notes_list(self, ctx:commands.Context, user:discord.User=None):
        user = ctx.author if not user else user
        notes = await self.bot.postgres.fetch("SELECT * FROM notes WHERE user_id=$1", user.id)
        notelistmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        notelistmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
        if not notes: 
            notelistmbed.title = F"{user} doesn't have any note"
            return await ctx.reply(embed=notelistmbed)
        tasks = []
        counter = 0
        for stuff in notes:
            tasks.append(F"[{counter}.]({stuff['jump_url']}) {stuff['task']}\n")
            counter += 1
        notelistmbed.title=F"{user.name}'s notes:"
        notelistmbed.description="".join(task for task in tasks)
        await ctx.reply(embed=notelistmbed)

    # Notes-Add
    @notes.command(name="add", aliases=["ad"], help="Adds the given task to your notes")
    async def notes_add(self, ctx:commands.Context, *, task:str):
        note = await self.bot.postgres.fetchval("SELECT task FROM notes WHERE task=$1 AND user_id=$2", task, ctx.author.id)
        noteaddmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        noteaddmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
        if note:
            noteaddmbed.title = "Is already in your notes:"
            noteaddmbed.description = F"{task}"
            return await ctx.reply(embed=noteaddmbed)
        await self.bot.postgres.execute("INSERT INTO notes(user_name,user_id,task,jump_url) VALUES($1,$2,$3,$4)", ctx.author.name, ctx.author.id, task, ctx.message.jump_url)
        noteaddmbed.title = "Added:"
        noteaddmbed.description = F"{task}\n**To your notes**"
        await ctx.reply(embed=noteaddmbed)

    # Notes-Remove
    @notes.command(name="remove", aliases=["rm"], help="Removes the given task from your notes")
    async def notes_remove(self, ctx:commands.Context, *, number:int):
        notes = await self.bot.postgres.fetch("SELECT * FROM notes WHERE user_id=$1", ctx.author.id)
        noteremovembed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        noteremovembed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
        if not notes:
            noteremovembed.title = "You don't have any note"
            return await ctx.reply(embed=noteremovembed)
        tasks = []
        for stuff in notes:
            tasks.append(stuff["task"])
        if len(tasks) < number:
            noteremovembed.title = "Is not in your notes:"
            noteremovembed.description = F"{number}\n**Check your notes**"
            return await ctx.reply(embed=noteremovembed)
        await self.bot.postgres.execute("DELETE FROM notes WHERE user_id=$1 AND task=$2", ctx.author.id, tasks[number])
        noteremovembed.title = "Removed:"
        noteremovembed.description = F"{tasks[number]}\n**From your notes**"
        await ctx.reply(embed=noteremovembed)

    # Notes-Clear
    @notes.command(name="clear", aliases=["cr"], help="Clears your notes")
    async def notes_clear(self, ctx:commands.Context):
        notes = await self.bot.postgres.fetch("SELECT task FROM notes WHERE user_id=$1", ctx.author.id)
        noteclearmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        noteclearmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
        if not notes:
            noteclearmbed.title = "You don't have any note"
            return await ctx.reply(embed=noteclearmbed)
        view = confirm.ViewConfirm(ctx)
        view.message = await ctx.reply(content="Are you sure if you want to clear everything:", view=view)
        await view.wait()
        if view.value:
            tasks = []
            for stuff in notes:
                tasks.append(stuff["task"])
            for task in tasks:
                await self.bot.postgres.execute("DELETE FROM notes WHERE task=$1 AND user_id=$2", task, ctx.author.id)
            noteclearmbed.title = "Cleared:"
            noteclearmbed.description = "**Your notes**"
            await ctx.reply(embed=noteclearmbed)

    # Notes-Edit
    @notes.command(name="edit", aliases=["ed"], help="Edits the given task with the new given task")
    async def notes_edit(self, ctx:commands.Context, number:int, *, task:str):
        notes = await self.bot.postgres.fetch("SELECT task FROM notes WHERE user_id=$1", ctx.author.id)
        noteeditmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        noteeditmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
        if not notes:
            noteeditmbed.title = "You don't have any note"
            return await ctx.reply(embed=noteeditmbed)
        tasks = []
        for stuff in notes:
            tasks.append(stuff["task"])
        if len(tasks) < number:
            noteeditmbed.title = "Is not in your notes:"
            noteeditmbed.description = F"{number}\n**Check your notes**"
            return await ctx.reply(embed=noteeditmbed)
        await self.bot.postgres.execute("UPDATE notes SET task=$1, jump_url=$2 WHERE user_id=$3 AND task=$4", task, ctx.message.jump_url, ctx.author.id, tasks[number])
        noteeditmbed.title = "Edited:"
        noteeditmbed.description = F"**Before:** {tasks[number]}\n**After:** {task}"
        await ctx.reply(embed=noteeditmbed)

def setup(bot):
    bot.add_cog(Utility(bot))