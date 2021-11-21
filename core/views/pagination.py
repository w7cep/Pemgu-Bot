import discord

class ViewPagination(discord.ui.View):
    def __init__(self, ctx, pages):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.page = 0
        self.pages = pages

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.blurple, disabled=True)
    async def first(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.next.disabled: self.next.disabled = False
        if self.last.disabled: self.last.disabled = False
        button.disabled = True
        self.counter.label = F"0/{len(self.pages)}"
        await interaction.response.edit_message(embed=self.pages[0], view=button.view)

    @discord.ui.button(emoji="⏪", style=discord.ButtonStyle.green, disabled=True)
    async def previous(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.next.disabled: self.next.disabled = False
        if self.last.disabled: self.last.disabled = False
        self.page -= 1
        if self.page == 0: button.disabled = True
        self.counter.label = F"{self.page}/{len(self.pages)}"
        await interaction.response.edit_message(embed=self.pages[self.page], view=button.view)

    @discord.ui.button(emoji="⏹", style=discord.ButtonStyle.red)
    async def stop(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.message.delete()

    @discord.ui.button(emoji="⏩", style=discord.ButtonStyle.green, disabled=False)
    async def next(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.previous.disabled: self.previous.disabled = False
        if self.first.disabled: self.first.disabled = False
        self.page += 1
        if self.page >= (len(self.pages)-1):
            embed = self.pages[-1]
            button.disabled = True
        else: 
            embed = self.pages[self.page]
        self.counter.label = F"{self.page}/{len(self.pages)}"
        await interaction.response.edit_message(embed=embed, view=button.view)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.blurple, disabled=False)
    async def last(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.previous.disabled: self.previous.disabled = False
        if self.first.disabled: self.first.disabled = False
        if not self.next.disabled: self.next.disabled = True
        button.disabled = True
        self.counter.label = F"{len(self.pages)}/{len(self.pages)}"
        await interaction.response.edit_message(embed=self.pages[-1], view=button.view)

    @discord.ui.button(style=discord.ButtonStyle.gray, disabled=True)
    async def counter(self, button:discord.ui.Button, interaction:discord.Interaction):
        return

    async def start(self):
        self.counter.label = f"0/{len(self.pages)}"
        await self.ctx.reply(embed=self.pages[0], view=self) 

    async def on_timeout(self):
        if self.children:
            self.clear_items()
            await self.message.edit(content="Timed-out", view=self)

    async def interaction_check(self, interaction:discord.Interaction):
        if interaction.user.id != self.ctx.message.author.id:
            icheckmbed = discord.Embed(
                color=self.ctx.bot.color,
                title=F"You can't use this",
                description=F"{interaction.user.mention} - Only {self.ctx.author.mention} can use this\nCause they did the command\nIf you want to use this, do what they did",
                timestamp=interaction.message.created_at
            )
            icheckmbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=icheckmbed, ephemeral=True)
            return False
        return True