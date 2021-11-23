# Notes
@commands.group(name="notes", aliases=["note"], help="Taking notes with these, Consider using subcommands", invoke_without_command=True)
async def notes(self, ctx:commands.Context):
    await ctx.send_help("notes")

# Notes-List
@notes.command(name="list", aliases=["="], help="Shows every of your or the given user's notes")
async def notes_list(self, ctx:commands.Context, user:discord.User=None):
    user = ctx.author if not user else user
    notes = await self.bot.postgres.fetch("SELECT * FROM notes WHERE user_id=$1 ORDER BY position", user.id)
    notelistmbed = discord.Embed(
        color=self.bot.color,
        timestamp=ctx.message.created_at
    )
    notelistmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
    if not notes: 
        notelistmbed.title = F"{user} doesn't have any note"
        return await ctx.reply(embed=notelistmbed)
    notelistmbed.title=F"{user.name}'s notes:"
    notelistmbed.description="\n".join(F"[{n['position']}.]({n['jump_url']}) {n['note']}" for n in notes)
    await ctx.reply(embed=notelistmbed)

# Notes-Add
@notes.command(name="add", aliases=["+"], help="Adds the given note to your notes")
async def notes_add(self, ctx:commands.Context, *, note:str):
    notes = await self.bot.postgres.fetch("SELECT * FROM notes WHERE user_id=$1", ctx.author.id)
    noteaddmbed = discord.Embed(
        color=self.bot.color,
        timestamp=ctx.message.created_at
    )
    noteaddmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
    await self.bot.postgres.execute("INSERT INTO notes(position,user_name,user_id,note,jump_url) VALUES($1,$2,$3,$4,$5)", len(notes)+1, ctx.author.name, ctx.author.id, note, ctx.message.jump_url)
    noteaddmbed.title = "Successfully added:"
    noteaddmbed.description = F"{note}\n**To your notes**"
    await ctx.reply(embed=noteaddmbed)

# Notes-Remove
@notes.command(name="remove", aliases=["-"], help="Removes the note with the given position from your notes")
async def notes_remove(self, ctx:commands.Context, *, position:int):
    notes = await self.bot.postgres.fetch("SELECT * FROM notes WHERE user_id=$1", ctx.author.id)
    noteremovembed = discord.Embed(
        color=self.bot.color,
        timestamp=ctx.message.created_at
    )
    noteremovembed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
    if not notes:
        noteremovembed.title = "You don't have any note"
        return await ctx.reply(embed=noteremovembed)
    if len(notes) < position:
        noteremovembed.title = "Is not in your notes:"
        noteremovembed.description = F"{position}\n**Check your notes**"
        return await ctx.reply(embed=noteremovembed)
    await self.bot.postgres.execute("DELETE FROM notes WHERE user_id=$1 AND position=$2", ctx.author.id, position)
    noteremovembed.title = "Successfully removed:"
    noteremovembed.description = F"{position}\n**From your notes**"
    await ctx.reply(embed=noteremovembed)

# Notes-Clear
@notes.command(name="clear", aliases=["*"], help="Clears your notes")
async def notes_clear(self, ctx:commands.Context):
    notes = await self.bot.postgres.fetch("SELECT * FROM notes WHERE user_id=$1", ctx.author.id)
    noteclearmbed = discord.Embed(
        color=self.bot.color,
        timestamp=ctx.message.created_at
    )
    noteclearmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
    if not notes:
        noteclearmbed.title = "You don't have any note"
        return await ctx.reply(embed=noteclearmbed)
    view = Confirm(ctx)
    view.message = await ctx.reply(content="Are you sure if you want to clear everything:", view=view)
    await view.wait()
    if view.value:
        for note in notes:
            await self.bot.postgres.execute("DELETE FROM notes WHERE position=$1 AND user_id=$2", note['position'], ctx.author.id)
        noteclearmbed.title = "Successfully cleared:"
        noteclearmbed.description = "**Your notes**"
        await ctx.reply(embed=noteclearmbed)

# Notes-Edit
@notes.command(name="edit", aliases=["~"], help="Edits the given note with the new given note")
async def notes_edit(self, ctx:commands.Context, position:int, *, note:str):
    notes = await self.bot.postgres.fetch("SELECT * FROM notes WHERE user_id=$1", ctx.author.id)
    noteeditmbed = discord.Embed(
        color=self.bot.color,
        timestamp=ctx.message.created_at
    )
    noteeditmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar)
    if not notes:
        noteeditmbed.title = "You don't have any note"
        return await ctx.reply(embed=noteeditmbed)
    if len(notes) < position:
        noteeditmbed.title = "Is not in your notes:"
        noteeditmbed.description = F"{position}\n**Check your notes**"
        return await ctx.reply(embed=noteeditmbed)
    await self.bot.postgres.execute("UPDATE notes SET note=$1, jump_url=$2 WHERE user_id=$3 AND position=$4", note, ctx.message.jump_url, ctx.author.id, position)
    noteeditmbed.title = "Successfully edited:"
    noteeditmbed.description = F"{note}\n**In your notes**"
    await ctx.reply(embed=noteeditmbed)