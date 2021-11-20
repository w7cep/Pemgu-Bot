import discord

class ViewPagination(discord.ui.View):
    def __init__(self, ctx, embeds):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.embed = 0
        self.embeds = embeds
    
    @discord.ui.button(emoji="⏪", style=discord.ButtonStyle.green, disabled=True)
    async def previous(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.next.disabled: self.next.disabled = False
        self.embed -= 1
        if self.embed == 0: button.disabled = True
        await interaction.response.edit_message(embed=self.embeds[self.embed], view=button.view)

    @discord.ui.button(emoji="⏹", style=discord.ButtonStyle.red)
    async def stop(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.message.delete()

    @discord.ui.button(emoji="⏩", style=discord.ButtonStyle.green)
    async def next(self, button:discord.ui.Button, interaction:discord.Interaction):
        if self.previous.disabled: self.previous.disabled = False
        if len(self.embeds) <= self.embed: button.disabled = True
        else: self.embed += 1
        await interaction.response.edit_message(embed=self.embeds[self.embed], view=button.view)

    async def interaction_check(self, interaction:discord.Interaction):
        if interaction.user.id == self.ctx.message.author.id:
            return True
        else:
            icheckmbed = discord.Embed(
                color=self.ctx.bot.color,
                title=F"You can't use this",
                description=F"{interaction.user.mention} - Only {self.ctx.author.mention} can use this\nCause they did the command\nIf you want to use this, do what they did",
                timestamp=interaction.message.created_at
            )
            icheckmbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=icheckmbed, ephemeral=True)
            return False
