import discord, typing, datetime
from discord.ext import commands

class Moderation(commands.Cog, description="Was someone being bad?"):
    def __init__(self, bot):
        self.bot = bot

    # Ban
    @commands.command(name="ban", aliases=["bn"], help="Bans the given user")
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban(self, ctx:commands.Context, member:discord.Member, *, reason:str=None):
        reason = "Nothing was provided" if not reason else reason
        abnmbed = discord.Embed(
            color=self.bot.color,
            title=F"Banned:",
            description=F"{member.mention}\n{reason}",
            timestamp=ctx.message.created_at
        )
        abnmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        ubnmbed = discord.Embed(
            color=self.bot.color,
            title=F"Dear {member}\nBanned:",
            description=F"{ctx.guild}\n{ctx.author}\n{reason}",
            timestamp=ctx.message.created_at
        )
        ubnmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await member.send(embed=ubnmbed)
        await ctx.guild.ban(member, reason=F"{ctx.author}\n{reason}")
        await ctx.reply(embed=abnmbed)

    # Unban
    @commands.command(name="unban", aliases=["un"], help="Unbans the given user")
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def unban(self, ctx:commands.Context, user:discord.User, *, reason:str=None):
        reason = "Nothing was provided" if not reason else reason
        aunmbed = discord.Embed(
            color=self.bot.color,
            title=F"Unbanned:",
            description=F"{user.mention}\n{reason}",
            timestamp=ctx.message.created_at
        )
        aunmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        uunmbed = discord.Embed(
            color=self.bot.color,
            title=F"Dear {user}\nUnbanned:",
            description=F"{ctx.guild}\n{ctx.author}\n{reason}",
            timestamp=ctx.message.created_at
        )
        uunmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await user.send(embed=uunmbed)
        await ctx.guild.unban(user)
        await ctx.reply(embed=aunmbed)

    # Kick
    @commands.command(name="kick", aliases=["kc"], help="Kicks the given user")
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    async def kick(self, ctx:commands.Context, member:discord.Member, *, reason:str=None):
        reason = "Nothing was provided" if not reason else reason
        akcmbed = discord.Embed(
            color=self.bot.color,
            title=F"Kicked:",
            description=F"{member.mention}\n{reason}",
            timestamp=ctx.message.created_at
        )
        akcmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        ukcmbed = discord.Embed(
            color=self.bot.color,
            title=F"Dear {member}\nKicked:",
            description=F"{ctx.guild}\n{ctx.author}\n{reason}",
            timestamp=ctx.message.created_at
        )
        ukcmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await member.send(embed=ukcmbed)
        await ctx.guild.kick(user=member, reason=reason)
        await ctx.reply(embed=akcmbed)

    # AddRole
    @commands.command(name="addrole", aliases=["ae"], help="Adds the given role to the given user")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def addrole(self, ctx:commands.Context, role:discord.Role, member:discord.Member=None):
        member = ctx.author if not member else member
        aembed = discord.Embed(
            color=self.bot.color,
            description=F"{member.mention}\n{role.mention}",
            timestamp=ctx.message.created_at
        )
        aembed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if role.position > ctx.author.top_role.position:
            aembed.title = F"{role} is higher than {member}"
            return await ctx.reply(embed=aembed)
        if role in member.roles:
            aembed.title = "Already has:"
            return await ctx.reply(embed=aembed)
        await member.add_roles(role)
        aembed.title = "Added:"
        await ctx.reply(embed=aembed)
    
    # RemoveRole
    @commands.command(name="removerole", aliases=["re"], help="Removes the given role from the given user")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True)
    async def removerole(self, ctx:commands.Context, role:discord.Role, member:discord.Member=None):
        member = ctx.author if not member else member
        rembed = discord.Embed(
            color=self.bot.color,
            description=F"{member.mention}\n{role.mention}",
            timestamp=ctx.message.created_at
        )
        rembed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if role.position > ctx.author.top_role.position:
            rembed.title = F"{role} is higher than {member}"
            return await ctx.reply(embed=rembed)
        if role in member.roles:
            await member.remove_roles(role)
            rembed.title = "Removed:"
            return await ctx.reply(embed=rembed)
        rembed.title = "Doesn't have:"
        await ctx.reply(embed=rembed)

    # Slowmode
    @commands.command(name="slowmode", aliases=["sm"], help="Changes the slowmode of this or the given channel to the given seconds")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def slowmode(self, ctx:commands.Context, seconds:int, channel:discord.TextChannel=None):
        channel = ctx.channel if not channel else channel
        smmbed = discord.Embed(
            color=self.bot.color,
            description=F"{channel.mention}\n{datetime.timedelta(seconds=seconds)}",
            timestamp=ctx.message.created_at
        )
        smmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if seconds > 21600:
            smmbed.title = F"Seconds cannot be more than 21600"
            return await ctx.reply(embed=smmbed)
        if channel.slowmode_delay == seconds:
            smmbed.title = "Channel is already at the same slowmode:"
            return await ctx.reply(embed=smmbed)
        await channel.edit(reason=F"Channel: {channel.mention}\nSeconds: {datetime.timedelta(seconds=seconds)}\nBy: {ctx.author}", slowmode_delay=seconds)
        smmbed.title = "Changed the slowdown:"
        await ctx.reply(embed=smmbed)

    # Lock
    @commands.command(name="lock", aliases=["lc"], help="Locks this or the given channel")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def lock(self, ctx:commands.Context, channel:typing.Union[discord.TextChannel, discord.StageChannel, discord.VoiceChannel]=None):
        channel = ctx.channel if not channel else channel
        over = channel.overwrites_for(ctx.guild.default_role)
        over.connect = False
        over.speak = False
        over.request_to_speak = False
        over.send_messages = False
        over.add_reactions = False
        over.create_public_threads = False
        over.create_private_threads = False
        lcmbed = discord.Embed(
            color=self.bot.color,
            description=channel.mention,
            timestamp=ctx.message.created_at
        )
        lcmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not channel.permissions_for(ctx.guild.default_role).send_messages:
            lcmbed.title = "Is already locked:"
            return await ctx.reply(embed=lcmbed)
        else:
            await channel.set_permissions(ctx.guild.default_role, overwrite=over)
            lcmbed.title = "Locked:"
            await ctx.reply(embed=lcmbed)

    # Unlock
    @commands.command(name="unlock", aliases=["ulc"], help="Unlocks this or the given channel")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def unlock(self, ctx:commands.Context, channel:typing.Union[discord.TextChannel, discord.StageChannel, discord.VoiceChannel]=None):
        channel = ctx.channel if not channel else channel
        over = channel.overwrites_for(ctx.guild.default_role)
        over.connect = False
        over.speak = False
        over.request_to_speak = False
        over.send_messages = False
        over.add_reactions = False
        over.create_public_threads = False
        over.create_private_threads = False
        ulcmbed = discord.Embed(
            color=self.bot.color,
            description=channel.mention,
            timestamp=ctx.message.created_at
        )
        ulcmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if channel.permissions_for(ctx.guild.default_role).send_messages:
            ulcmbed.title = "Is already unlocked:"
            return await ctx.reply(embed=ulcmbed)
        else:
            await channel.set_permissions(ctx.guild.default_role, overwrite=over)
            ulcmbed.title = "Unlocked:"
            await ctx.reply(embed=ulcmbed)

    # Mute
    @commands.command(name="mute", aliases=["mt"], help="Mutes  or Unmutes the given user")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @commands.bot_has_guild_permissions(manage_roles=True, manage_channels=True)
    async def mute(self, ctx:commands.Context, member:discord.Member, *, reason:str=None):
        reason = "Nothing was provided" if not reason else reason
        mtmbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        mtmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        muterole = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muterole:
            muterole = await ctx.guild.create_role(
                color=discord.Color.red(),
                name="Muted",
                mentionable=True,
                reason="There was no Muted role, so I created one."
            )
            crmtmbed = discord.Embed(
                color=self.bot.color,
                title=F"There was no Muted role, so I created one",
                description=muterole.mention,
                timestamp=ctx.message.created_at
            )
            crmtmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=crmtmbed)
            for channel in ctx.guild.channels:
                await channel.set_permissions(muterole, add_reactions=False, send_messages=False, connect=False, speak=False, create_public_threads=False, create_private_threads=False)
        if muterole in member.roles:
            mtmbed.title = F"UnMuted:"
            mtmbed.description = F"UnMuted: {member.mention}\n{reason}\n{muterole.mention}"
            await member.remove_roles(muterole, reason=F"Un{ctx.author}\n{reason}")
            await ctx.reply(embed=mtmbed)
        else:
            mtmbed.title = F"Muted:"
            mtmbed.description = F"{member.mention}\n{reason}\n{muterole.mention}"
            await member.add_roles(muterole, reason=F"{ctx.author}\n{reason}")
            await ctx.reply(embed=mtmbed)

    # Clear
    @commands.command(name="clear", aliases=["cr"], help="Deletes messages with the given amount")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    async def clear(self, ctx:commands.Context, *, amount:int):
        pumbed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        pumbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if amount > 100:
            pumbed.title = "Can't clear more than 100 messages"
            return await ctx.reply(embed=pumbed, delete_after=5)
        await ctx.channel.purge(limit=amount+1)
        pumbed.title = F"Deleted {amount} amount of messages"
        await ctx.reply(embed=pumbed, delete_after=5)

    # EmojiAdd
    @commands.command(name="emojiadd", aliases=["ea"], help="Creates a emoji based on the given name and image")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_emojis=True)
    @commands.bot_has_guild_permissions(manage_emojis=True)
    async def emojiadd(self, ctx:commands.Context, name:str):
        eambed = discord.Embed(
            color=self.bot.color,
            timestamp=ctx.message.created_at
        )
        eambed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        if not len(ctx.message.attachments) > 0:
            eambed.title = "You need to provide an image"
            return await ctx.reply(embed=eambed)
        emoji = await ctx.guild.create_custom_emoji(name=name, image=(await ctx.message.attachments[0].read()), reason=F"Added by: {ctx.author}")
        eambed.title = "Created the emoji:"
        eambed.set_image(url=emoji.url)
        await ctx.reply(embed=eambed)

    # EmojiRemove
    @commands.command(name="emojiremove", aliases=["er"], help="Removes the given emoji")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_emojis=True)
    @commands.bot_has_guild_permissions(manage_emojis=True)
    async def emojiremove(self, ctx:commands.Context, emoji:discord.Emoji):
        ermbed = discord.Embed(
            color=self.bot.color,
            title="Removed the emoji:",
            timestamp=ctx.message.created_at
        )
        ermbed.set_image(url=emoji.url)
        ermbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
        await emoji.delete()
        await ctx.reply(embed=ermbed)

def setup(bot):
    bot.add_cog(Moderation(bot))