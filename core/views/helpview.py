import discord

class SelectUI(discord.ui.Select):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.help = view.help
        self.mapping = view.mapping
        self.homepage = view.homepage

    def gts(self, command):
        return F"• **{command.qualified_name}** {command.signature} - {command.help or 'No help found...'}\n"

    async def callback(self, interaction:discord.Interaction):
        for cog, commands in self.mapping.items():
            if self.values[0] == cog.qualified_name:
                mbed = discord.Embed(
                    color=self.help.context.bot.color,
                    title=F"{self.help.emojis.get(cog.qualified_name) if self.help.emojis.get(cog.qualified_name) else '❓'} {cog.qualified_name}",
                    description=F"{cog.description}\n\n{''.join(self.gts(command) for command in cog.walk_commands())}",
                    timestamp=self.help.context.message.created_at
                )
                mbed.set_thumbnail(url=self.help.context.me.display_avatar.url)
                mbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
                mbed.set_footer(text="<> is required | [] is optional")
                await interaction.response.edit_message(embed=mbed)

class SelectView(discord.ui.View):
    def __init__(self, help, mapping):
        super().__init__(timeout=None)
        self.help = help
        self.mapping = mapping
        self.homepage = discord.Embed(
            color=self.help.context.bot.color,
            title=F"{self.help.context.me.name}'s Help",
            description="For more help or information use the menu.",
            timestamp=self.help.context.message.created_at
        )
        options = []
        for cog, commands in self.mapping.items():
            if cog and not cog.qualified_name.startswith("On") and not cog.qualified_name in self.help.context.bot._others:
                option = discord.SelectOption(emoji=self.help.emojis.get(cog.qualified_name) if self.help.emojis.get(cog.qualified_name) else '❓', label=F"{cog.qualified_name} Category", description=cog.description, value=cog.qualified_name)
                options.append(option)
        self.add_item(item=SelectUI(placeholder="Where do you want to go...", options=options, min_values=1, max_values=1, view=self))
        self.add_item(item=discord.ui.Button(emoji="➕", label="Invite", url=discord.utils.oauth_url(client_id=self.help.context.me.id, scopes=('bot', 'applications.commands'), permissions=discord.Permissions(administrator=True))))
        self.add_item(item=discord.ui.Button(emoji="👨‍💻", label="Github", url="https://github.com/lvlahraam/Pemgu-Bot"))

    @discord.ui.button(emoji="🏠", label="Home", style=discord.ButtonStyle.green)
    async def home(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.edit_message(embed=self.homepage)

    @discord.ui.button(emoji="💣", label="Delete", style=discord.ButtonStyle.red)
    async def delete(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.message.delete()

    async def on_timeout(self):
        try:
            for item in self.children:
                if isinstance(item, discord.ui.Select):
                    item.placeholder = "Disabled due to being timed out..."
                item.disabled = True
            await self.message.edit(view=self)
        except discord.NotFound:
            return

    async def interaction_check(self, interaction:discord.Interaction):
        if interaction.user.id == self.help.context.author.id:
            return True
        icheckmbed = discord.Embed(
            color=self.help.context.bot.color,
            title="You can't use this",
            description=F"{interaction.user.mention} - Only {self.help.context.author.mention} can use that\nCause they did the command\nIf you wanted to use the command, do what they did",
            timestamp=self.help.context.message.created_at
        )
        icheckmbed.set_thumbnail(url=self.help.context.me.display_avatar.url)
        icheckmbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=icheckmbed, ephemeral=True)
        return False

class ButtonUI(discord.ui.Button):
    def __init__(self, view, **kwargs):
        super().__init__(**kwargs)
        self.help = view.help
        self.mapping = view.mapping
        self.homepage = view.homepage

    def gts(self, command):
        return F"• **{command.qualified_name}** {command.signature} - {command.help or 'No help found...'}\n"

    async def callback(self, interaction:discord.Interaction):
        for cog, commands in self.mapping.items():
            name = cog.qualified_name if cog else "Alone"
            description = cog.description if cog else "Commands without category"
            cmds = cog.walk_commands() if cog else commands
            if self.custom_id == name:
                mbed = discord.Embed(
                    color=self.help.context.bot.color,
                    title=F"{self.help.emojis.get(name) if self.help.emojis.get(name) else '❓'} {name} Category",
                    description=F"{description}\n\n{''.join(self.gts(command) for command in cmds)}",
                    timestamp=self.help.context.message.created_at
                )
                mbed.set_thumbnail(url=self.help.context.me.display_avatar.url)
                mbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
                mbed.set_footer(text="<> is required | [] is optional")
                await interaction.response.edit_message(embed=mbed)

class ButtonView(discord.ui.View):
    def __init__(self, help, mapping):
        super().__init__(timeout=None)
        self.help = help
        self.mapping = mapping
        self.homepage = discord.Embed(
            color=self.help.context.bot.color,
            title=F"{self.help.context.me.name}'s Help",
            description="For more help or information use and click on the buttons.",
            timestamp=self.help.context.message.created_at
        )
        for cog, commands in self.mapping.items():
            if cog and not cog.qualified_name.startswith("On") and cog.qualified_name not in self.help.context.bot._others:
                self.add_item(item=ButtonUI(emoji=self.help.emojis.get(cog.qualified_name), label=cog.qualified_name, style=discord.ButtonStyle.blurple, custom_id=cog.qualified_name, view=self))
        self.add_item(item=discord.ui.Button(emoji="➕", label="Invite", url=discord.utils.oauth_url(client_id=self.help.context.me.id, scopes=('bot', 'applications.commands'), permissions=discord.Permissions(administrator=True))))
        self.add_item(item=discord.ui.Button(emoji="👨‍💻", label="Github", url="https://github.com/lvlahraam/Pemgu-Bot"))

    @discord.ui.button(emoji="🏠", label="Home", style=discord.ButtonStyle.green)
    async def home(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.response.edit_message(embed=self.homepage)

    @discord.ui.button(emoji="💣", label="Delete", style=discord.ButtonStyle.red)
    async def delete(self, button:discord.ui.Button, interaction:discord.Interaction):
        await interaction.message.delete()

    async def interaction_check(self, interaction:discord.Interaction):
        if interaction.user.id == self.help.context.author.id: return True
        icheckmbed = discord.Embed(
            color=self.help.context.bot.color,
            title="You can't use this",
            description=F"{interaction.user.mention} - Only {self.help.context.author.mention} can use that\nCause they did the command\nIf you wanted to use the command, do what they did",
            timestamp=self.help.context.message.created_at
        )
        icheckmbed.set_thumbnail(url=self.help.context.me.display_avatar.url)
        icheckmbed.set_author(name=interaction.user, icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=icheckmbed, ephemeral=True)
        return False