import discord
from discord.ext import commands
from core.views.confirm import Confirm

class Notes(commands.Cog, description="Taking notes with these!"):
    def __init__(self, bot):
        self.bot = bot
    
        # Notes
    @commands.group(name="notes", aliases=["note"], help="Consider using subcommands", invoke_without_command=True)
    async def notes(self, ctx:commands.Context):
        await ctx.send_help("notes")

    # Notes-List
    @notes.command(name="list", aliases=["="], help="Will show every of your or the given user's notes")
    async def notes_list(self, ctx:commands.Context, user:discord.User=None):
        user = ctx.author if not user else user
        notes = await self.bot.postgres.fetch("SELECT task FROM notes WHERE user_id=$1", user.id)
        notelistmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        notelistmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
        if not notes: 
            notelistmbed.title = F"{user} doesn't have any note"
            return await ctx.send(embed=notelistmbed)
        tasks = []
        counter = 0
        for stuff in notes:
            tasks.append(F"`[#{counter}].` {stuff['task']}\n")
            counter += 1
        notelistmbed.title=F"{user}'s notes:"
        notelistmbed.description="".join(task for task in tasks)
        await ctx.send(embed=notelistmbed)

    # Notes-Add
    @notes.command(name="add", aliases=["+"], help="Will add the given task to your notes")
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
            return await ctx.send(embed=noteaddmbed)
        await self.bot.postgres.execute("INSERT INTO notes(user_name,user_id,task) VALUES($1,$2,$3)", ctx.author.name, ctx.author.id, task)
        noteaddmbed.title = "Successfully added:"
        noteaddmbed.description = F"{task}\n**To your notes**"
        await ctx.send(embed=noteaddmbed)

    # Notes-Remove
    @notes.command(name="remove", aliases=["-"], help="Will remove the given task from your notes")
    async def notes_remove(self, ctx:commands.Context, *, number:int):
        notes = await self.bot.postgres.fetch("SELECT * FROM notes WHERE user_id=$1", ctx.author.id)
        noteremovembed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        noteremovembed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
        if not notes:
            noteremovembed.title = "You don't have any note"
            return await ctx.send(embed=noteremovembed)
        tasks = []
        for stuff in notes:
            tasks.append(stuff["task"])
        if len(tasks) < number:
            noteremovembed.title = "Is not in your notes:"
            noteremovembed.description = F"{number}\n**Check your notes**"
            return await ctx.send(embed=noteremovembed)
        await self.bot.postgres.execute("DELETE FROM notes WHERE user_id=$1 AND task=$2", ctx.author.id, tasks[number])
        noteremovembed.title = "Successfully removed:"
        noteremovembed.description = F"{tasks[number]}\n**From your notes**"
        await ctx.send(embed=noteremovembed)

    # Notes-Clear
    @notes.command(name="clear", aliases=["*"], help="Will clear your notes")
    async def notes_clear(self, ctx:commands.Context):
        notes = await self.bot.postgres.fetch("SELECT task FROM notes WHERE user_id=$1", ctx.author.id)
        noteclearmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        noteclearmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
        if not notes:
            noteclearmbed.title = "You don't have any note"
            return await ctx.send(embed=noteclearmbed)
        view = Confirm(ctx)
        view.message = await ctx.send(content="Are you sure if you want to clear everything:", view=view)
        await view.wait()
        if view.value:
            tasks = []
            for stuff in notes:
                tasks.append(stuff["task"])
            for task in tasks:
                await self.bot.postgres.execute("DELETE FROM notes WHERE task=$1 AND user_id=$2", task, ctx.author.id)
            noteclearmbed.title = "Successfully cleared:"
            noteclearmbed.description = "**Your notes**"
            await ctx.send(embed=noteclearmbed)

    # Notes-Edit
    @notes.command(name="edit", aliases=["~"], help="Will edit the given task with the new given task")
    async def notes_edit(self, ctx:commands.Context, number:int, *, task:str):
        notes = await self.bot.postgres.fetch("SELECT task FROM notes WHERE user_id=$1", ctx.author.id)
        noteeditmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        noteeditmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
        if not notes:
            noteeditmbed.title = "You don't have any note"
            return await ctx.send(embed=noteeditmbed)
        tasks = []
        for stuff in notes:
            tasks.append(stuff["task"])
        if len(tasks) < number:
            noteeditmbed.title = "Is not in your notes:"
            noteeditmbed.description = F"{number}\n**Check your notes**"
            return await ctx.send(embed=noteeditmbed)
        await self.bot.postgres.execute("UPDATE notes SET task=$1 WHERE user_id=$2 AND task=$3", task, ctx.author.id, tasks[number])
        noteeditmbed.title = "Successfully edited:"
        noteeditmbed.description = F"**Before:** {tasks[number]}\n**After:** {task}"
        await ctx.send(embed=noteeditmbed)

def setup(bot):
    bot.add_cog(Notes(bot))