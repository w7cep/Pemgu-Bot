import discord, difflib, traceback
from discord.ext import commands

class DYMButtons(discord.ui.Button):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.ctx = view.ctx
        self.matches = view.matches
    async def callback(self, interaction:discord.Interaction):
        for match in self.matches:
            if self.label == match:
                await interaction.message.delete()
                command = self.ctx.bot.get_command(match)
                await self.ctx.invoke(command)
        if self.label == "Delete":
            deletembed = discord.Embed(
                color=self.ctx.bot.color,
                title="Deleted the message",
                timestamp=interaction.message.created_at
            )
            deletembed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
            await interaction.message.delete()
            await interaction.response.send_message(embed=deletembed, ephemeral=True)
class DYMView(discord.ui.View):
    def __init__(self, ctx, matches):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.matches = matches
        for match in self.matches:
            self.add_item(item=DYMButtons(label=match, style=discord.ButtonStyle.green, view=self))
        self.add_item(item=DYMButtons(emoji="💣",label="Delete", style=discord.ButtonStyle.red, custom_id="Delete", view=self))
    async def on_timeout(self):
        try:
            if self.children:
                for item in self.children:
                    self.clear_items()
                    self.add_item(discord.ui.Button(emoji="❌", label="You took so long to answer...", style=discord.ButtonStyle.blurple, disabled=True))
                    self.add_item(discord.ui.Button(emoji="💣", label="Disabled due to timeout...", style=discord.ButtonStyle.red, disabled=True))
                    await self.message.edit(view=self)
        except discord.NotFound:
            pass
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

class OnError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx:commands.Context, error:commands.CommandError):
        if isinstance(error, commands.CommandInvokeError): error = error.original
        print("".join(traceback.format_exception(type(error), error,  error.__traceback__)))
        errormbed = discord.Embed(
            color=self.bot.color,
            title=F"❌ An Error Occurred: {ctx.command}",
            description=F"- {error}",
            timestamp=ctx.message.created_at
        )
        errormbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=errormbed)
    
def setup(bot):
    bot.add_cog(OnError(bot))