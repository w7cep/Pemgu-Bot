  	# Imports

import discord
import logging
from unidecode import unidecode
import os
import aiohttp
import random
import errors
from datetime import datetime
import yaml
import random
import pickle
from pathlib import Path
import ast
import re
import inspect
from discord import activity
from discord.ext import commands, tasks
import DiscordUtils
import asyncpg
import typing
import asyncpraw
from discord import Interaction
from typing import (
    List,
    Optional
)
from asyncdagpi import Client, ImageFeatures

def source(o):
    s = inspect.getsource(o).split("\n")
    indent = len(s[0]) - len(s[0].lstrip())
    return "\n".join(i[indent:] for i in s)


def ready():
  source_ = source(discord.gateway.DiscordWebSocket.identify)
  patched = re.sub(
      r'([\'"]\$browser[\'"]:\s?[\'"]).+([\'"])',
      r"\1Discord Android\2",
      source_
  )
  loc = {}
  exec(compile(ast.parse(patched), "<string>", "exec"),
       discord.gateway.__dict__, loc)
  discord.gateway.DiscordWebSocket.identify = loc["identify"]

with open(r'/root/stealthbot/config.yaml') as file:
    full_yaml = yaml.load(file)
yaml_data = full_yaml

PRE = ('sb!',)
target_type = typing.Union[discord.Member, discord.User, discord.PartialEmoji, discord.Guild, discord.Invite]

# async def get_pre(client, message):
#     if not message.guild:
#         return commands.when_mentioned_or(DEFAULT_PREFIX)(client, message)
#     prefix = await client.db.fetchval('SELECT prefix FROM guilds WHERE guild_id = $1', message.guild.id)
#     if await client.is_owner(message.author) and client.no_prefix == True:
#         if prefix:
#             return commands.when_mentioned_or(prefix, "")(client, message)
#         else:
#             return commands.when_mentioned_or(DEFAULT_PREFIX, "")(client, message)
#     if not prefix:
#         prefix = DEFAULT_PREFIX
#     return commands.when_mentioned_or(prefix)(client, message)

class ConfirmButton(discord.ui.Button):
    def __init__(self, label: str, emoji: str, button_style: discord.ButtonStyle):
        super().__init__(style=button_style, label=label, emoji=emoji, )

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: Confirm = self.view
        view.value = True
        view.stop()


class CancelButton(discord.ui.Button):
    def __init__(self, label: str, emoji: str, button_style: discord.ButtonStyle):
        super().__init__(style=button_style, label=label, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: Confirm = self.view
        view.value = False
        view.stop()


class Confirm(discord.ui.View):
    def __init__(self, buttons: typing.Tuple[typing.Tuple[str]], timeout: int = 30):
        super().__init__(timeout=timeout)
        self.message = None
        self.value = None
        self.ctx: CustomContext = None
        self.add_item(ConfirmButton(emoji=buttons[0][0],
                                    label=buttons[0][1],
                                    button_style=(
                                            buttons[0][2] or discord.ButtonStyle.green
                                    )))
        self.add_item(CancelButton(emoji=buttons[1][0],
                                   label=buttons[1][1],
                                   button_style=(
                                           buttons[1][2] or discord.ButtonStyle.red
                                   )))

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user and interaction.user.id in (self.ctx.bot.owner_id, self.ctx.author.id):
            return True
        messages = [
            "Oh no you can't do that! This belongs to **{user}**",
            'This is **{user}**\'s confirmation, sorry! 💖',
            '😒 Does this look yours? **No**. This is **{user}**\'s confirmation button',
            '<a:stopit:891139227327295519>',
            'HEYYYY!!!!! this is **{user}**\'s menu.',
            'Sorry but you can\'t mess with **{user}**\' menu QnQ',
            'No. just no. This is **{user}**\'s menu.',
            '<:blobstop:749111017778184302>' * 3,
            'You don\'t look like {user} do you...',
            '🤨 Thats not yours! Thats **{user}**\'s',
            '🧐 Whomst! you\'re not **{user}**',
            '_out!_ 👋'
        ]
        await interaction.response.send_message(random.choice(messages).format(user=self.ctx.author.display_name),
                                                ephemeral=True)

        return False

class CustomContext(commands.Context):

    @staticmethod
    def tick(option : bool):
        ticks = {
            True: '<:greenTick:895688440690147370>',
            False: '<:redTick:895688440568508518>',
            None: '<:greyTick:895688440690114560>'}
        
        emoji = ticks.get(option, "<:redTick:596576672149667840>")
        return emoji

    @staticmethod
    def toggle(option : bool):
        ticks = {
            True: '<:toggle_on:896743740285263892>',
            False: '<:toggle_off:896743704323309588>',
            None: '<:toggle_off:896743704323309588>'}
        
        emoji = ticks.get(option, "<:toggle_off:896743704323309588>")
        return emoji
    
    @staticmethod
    def time(days : int, hours : int, minutes : int, seconds : int):
        def remove_s(string):
            if re.match(r"\d+", string).group() == "1":
                return string[:-1]
            return string
        
        days = remove_s(f"{days} days")
        hours = remove_s(f"{hours} hours")
        minutes = remove_s(f"{minutes} minutes")
        seconds = remove_s(f"{seconds} seconds")
        
        return " and ".join(", ".join(filter(lambda i: int(i[0]), (days, hours, minutes, seconds))).rsplit(", ", 1))
        
    @staticmethod
    def times(seconds : int):
        def make_str(value: int, unit: str):
            if value == 1: unit = unit[:-1]
            return f"{value} {unit}"
        
        days, remainder = make_str(seconds // 86400, "days"), seconds % 86400
        hours, remainder = make_str(remainder // 3600, "hours"), remainder % 3600
        minutes, remainder = make_str(remainder // 60, "minutes"), remainder % 60
        seconds = make_str(remainder, "seconds")
        
        return " and ".join(", ".join(filter(lambda i: int(i[0]), (days, hours, minutes, seconds))).rsplit(", ", 1))

    async def send(self, content : str=None, embed : discord.Embed=None, reminders : bool=True,
                   reply : bool=True, footer : bool=True, timestamp : bool=True, color : bool=True,
                   reference : typing.Union[discord.Message, discord.MessageReference]=None, **kwargs):

        reference = (reference or self.message.reference or self.message) if reply is True else reference
        
        if embed:
            
            if footer == True:
                embed.set_footer(text=f"Requested by {self.author}", icon_url=self.author.display_avatar.url)
                
            if timestamp == True:
                embed.timestamp = discord.utils.utcnow()
                
            if color == True:
                colors = [0x910023, 0xA523FF]
                color = random.choice(colors)
                embed.color = color
                
        if reminders == True:
            
            answers = [":star: Support **Stealth Bot** by voting on top.gg: <https://top.gg/bot/760179628122964008>",
                        ":star: Haven't voted for **Stealth Bot** yet? Make sure to vote on top.gg: <https://top.gg/bot/760179628122964008>",
                        ":star: A feature isn't working like it's supposed to? Join the **support server**: <https://discord.gg/MrBcA6PZPw>"]
            
            answer = random.choice(answers)
            number = random.randint(1, 40)
            
            content = content
            
            if number == 1:
                content = f"{answer}\n\n{str(content) if content else ''}"
            
        try:
            return await super().send(content=content, embed=embed, reference=reference, **kwargs)
        except discord.HTTPException:
            return await super().send(content=content, embed=embed, reference=None, **kwargs)
        
    async def confirm(self, message : str = "Do you want to confirm?", embed : discord.Embed=None, # added embed so it's possible to use ctx.confirm with an embed instead of a lame class normal message - P3ter
                      buttons : typing.Tuple[typing.Union[discord.PartialEmoji, str],
                                            str, discord.ButtonStyle] = None, timeout: int = 30,
                      delete_after_confirm: bool = False, delete_after_timeout: bool = False,
                      delete_after_cancel: bool = None):
        delete_after_cancel = delete_after_cancel if delete_after_cancel is not None else delete_after_confirm
        view = Confirm(buttons=buttons or (
            (None, 'Confirm', discord.ButtonStyle.green),
            (None, 'Cancel', discord.ButtonStyle.red)
        ), timeout=timeout)
        view.ctx = self
        if embed and message: # checks if there was BOTH embed and message and if there wasnt:
          message = await self.send(message, view=view, embed=embed)
        elif embed: # checks if there was an embed and if there wasnt:
          message = await self.send(view=view, embed=embed)
        else: # sends the message alone and if it was None it sends the default one "Do you want to confirm?"
          message = await self.send(message, view=view)
        await view.wait()
        
        if view.value is None:
            try:
                (await message.edit(view=None)) if \
                    delete_after_timeout is False else (await message.delete())
            except (discord.Forbidden, discord.HTTPException):
                pass
            return False
        
        elif view.value:
            try:
                (await message.edit(view=None)) if \
                    delete_after_confirm is False else (await message.delete())
            except (discord.Forbidden, discord.HTTPException):
                pass
            return True
        
        else:
            try:
                (await message.edit(view=None)) if \
                    delete_after_cancel is False else (await message.delete())
            except (discord.Forbidden, discord.HTTPException):
                pass
            return False

    async def trigger_typing(self) -> None:
        try:
            await super().trigger_typing()
            
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def dagpi(self, target: target_type = None, *, feature: ImageFeatures, **kwargs) -> discord.File:
        await self.trigger_typing()
        target = target or self.reference
        return await self.bot.dagpi_request(self, target, feature=feature, **kwargs)

    @property
    def reference(self) -> typing.Optional[discord.Message]:
        return getattr(self.message.reference, 'resolved', None)

class StealthBot(commands.AutoShardedBot):
    PRE: tuple = ("sb!",)
    def __init__(self, *args, **kwargs):
        super().__init__(command_prefix=self.get_pre, *args, **kwargs)

    async def get_pre(self, bot, message : discord.Message, raw_prefix : Optional[bool] = False):
        if not message:
            return commands.when_mentioned_or(*self.PRE)(bot, message) if not raw_prefix else self.PRE
        
        if not message.guild:
            return commands.when_mentioned_or(*self.PRE)(bot, message) if not raw_prefix else self.PRE
        
        try:
            prefix = self.prefixes[message.guild.id]
            
        except KeyError:
            prefix = (await self.db.fetchval("SELECT prefix FROM guilds WHERE guild_id = $1",
                                             message.guild.id)) or self.PRE
            prefix = prefix if prefix[0] else self.PRE

            self.prefixes[message.guild.id] = prefix

        if await bot.is_owner(message.author) and bot.no_prefix is True:
            return commands.when_mentioned_or(*prefix, "")(bot, message) if not raw_prefix else prefix
        return commands.when_mentioned_or(*prefix)(bot, message) if not raw_prefix else prefix
    
    async def get_context(self, message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)
    
    async def dagpi_request(self, ctx, target : target_type=None, *, feature:  ImageFeatures, **kwargs):
        bucket = client.dagpi_cooldown.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(commands.Cooldown(60, 60), retry_after, commands.BucketType.default)
        target = target or ctx.author
        url = getattr(target, "display_avatar", None) or getattr(target, "icon", None) or getattr(target, "guild", None) or target
        url = getattr(getattr(url, "icon", url), "url", url)
        request = await client.dagpi.image_process(feature, url, **kwargs)
        return discord.File(fp=request.image, filename=f"{str(feature)}.{request.format}")

client = StealthBot(
    activity=discord.Activity(type=discord.ActivityType.listening, name="sb!help"),
    intents = discord.Intents(
                            guild_reactions=True, # reaction add/remove/clear
                            guild_messages=True, # message create/update/delete
                            guilds=True, # guild/channel join/remove/update
                            integrations=True, # integrations update
                            voice_states=True, # voice state update
                            dm_reactions=True, # reaction add/remove/clear
                            guild_typing=True, # on typing
                            dm_messages=True, # message create/update/delete
                            presences=True, # member/user update for games/activities
                            dm_typing=True, # on typing 
                            webhooks=True, # webhook update
                            members=True, # member join/remove/update
                            invites=True, # invite create/delete
                            emojis=True, # emoji update
                            bans=True), # member ban/unban
    case_insensitive=True,
    help_command=None,
    enable_debug_events=True,
    strip_after_prefix=True,
    shard_count=3)

# Important stuff
client.tracker = DiscordUtils.InviteTracker(client)
client.allowed_mentions = discord.AllowedMentions.none()
client._BotBase__cogs = commands.core._CaseInsensitiveDict()
client.owner_ids = [564890536947875868, 555818548291829792, 349373972103561218] # 349373972103561218 (LeoCx1000) # 555818548291829792 (Vicente0670)

# Tokens
client.dagpi_cooldown = commands.CooldownMapping.from_cooldown(60, 60, commands.BucketType.default)
client.dagpi = Client(yaml_data['DAGPI_TOKEN'])
client.reddit = asyncpraw.Reddit(client_id=yaml_data['ASYNC_PRAW_CLIENT_ID'],
                                client_secret=yaml_data['ASYNC_PRAW_CLIENT_SECRET'],
                                user_agent=yaml_data['ASYNC_PRAW_USER_AGENT'],
                                username=yaml_data['ASYNC_PRAW_USERNAME'],
                                password=yaml_data['ASYNC_PRAW_PASSWORD'])

# Custom stuff
client.no_prefix = False
client.maintenance = False
client.launch_time = discord.utils.utcnow()
client.session = aiohttp.ClientSession(loop=client.loop)

# Cache stuff
client.afk_users = {}
client.auto_un_afk = {}
client.blacklist = {}
client.prefixes = {}
client.messages = {}
client.edited_messages = {}

# Useless stuff
client.brain_cells = 0
client.user_id = 760179628122964008
client.token = "haha no"

# Jishaku stuff
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"

	# Functions and stuff

async def create_db_pool():
    credentials = {"user": "postgres",
                   "password": "1211",
                   "database": "stealthdb",
                   "host": "localhost"}

    client.db = await asyncpg.create_pool(**credentials)
    print("connected to PostgreSQL")

    await client.db.execute("CREATE TABLE IF NOT EXISTS guilds(guild_id bigint PRIMARY KEY, prefix text);")

	# Tasks

@tasks.loop(minutes=120) # Task to notify the owners to bump the server every 120 minutes (2 hours)
async def bump(): # Makes a task called "bump"
    channel = client.get_channel(820049182860509206) # Gets the channel called "private_chat_for_meowsir_and_ender" (820049182860509206)
    await channel.send("<@596537151802572811> <@564890536947875868> DO `!d bump` RIGHT NOW OR I BREAK YOUR KNEECAP") # Tells the both owners to bump the server

@tasks.loop(minutes=5) # Task to change the VC every 5 minutes
async def change_vc(): # Makes a task called "change_vc"
    stealth_hangout = client.get_guild(799330949686231050)
    vc = client.get_channel(828651175585906759)
    await vc.edit(name=f"Members: {stealth_hangout.member_count}")

	# Events

@client.event
async def on_ready():
    change_vc.start() # Starts the task called "change_vc"

    print("started task: change_vc") # Prints "Started task: change_vc"
    print('-------------================----------------') # Prints some lines to make it look better
    print(f"connected to bot: {client.user.name}") # Prints "Connected to the bot {Name of the bot}"
    print(f"bot ID: {client.user.id}") # Prints "Bot ID {ID of the bot}"
    print('-------------================----------------') # Prints some lines to make it look better

    channel = client.get_channel(883658687867158529) # Get the channel called "bot_logs" (883658687867158529) and store it as the variable "channel"

    embed = discord.Embed(title="Bot started", color=0x2F3136) # Creates a embed with the title being "Bot started" and the color being 0x2F3136

    await channel.send(embed=embed) # Sends the embed in the channel

    await client.tracker.cache_invites() # Caches the invites

    print("tracker has been loaded")

# ---------------------------------------------------------------------------------------------- #

os.system('clear')

client.load_extension('jishaku')
print("jishaku has been loaded")


for filename in sorted(os.listdir('./cogs')): # For every file in the folder called "cogs"
    if filename.endswith('.py'): # If the file ends with .py
        client.load_extension(f'cogs.{filename[:-3]}') # Load the file as a extension/cog
        print(f'{filename[:-3]}.py has been loaded')
print('-------------================----------------')

# ---------------------------------------------------------------------------------------------- #

async def run_once_when_ready():
    await client.wait_until_ready()
    values = await client.db.fetch("SELECT user_id, is_blacklisted FROM blacklist")

    for value in values:
        client.blacklist[value['user_id']] = (value['is_blacklisted'] or False)
    print("blacklist system has been loaded")

    values = await client.db.fetch("SELECT guild_id, prefix FROM guilds")

    for value in values:
        if value['prefix']:
            client.prefixes[value['guild_id']] = ((value['prefix'] if value['prefix'][0] else PRE) or PRE)

    for guild in client.guilds:
        if not guild.unavailable:
            try:
                client.prefixes[guild.id]
            except KeyError:
                client.prefixes[guild.id] = PRE
                
    client.afk_users = dict([(r['user_id'], True) for r in (await client.db.fetch('SELECT user_id, start_time FROM afk')) if r['start_time']])
    client.auto_un_afk = dict([(r['user_id'], r['auto_un_afk']) for r in (await client.db.fetch('SELECT user_id, auto_un_afk FROM afk')) if r['auto_un_afk'] is not None])
                
@client.check
def maintenance(ctx):
    if client.maintenance is False:
        return True
    else:
        if ctx.author.id == 564890536947875868:
            return True
        else:
            raise errors.BotMaintenance

@client.check
def blacklist(ctx):
    try:
        is_blacklisted = client.blacklist[ctx.author.id]
    except KeyError:
        is_blacklisted = False
    if ctx.author.id == client.owner_id:
        is_blacklisted = False

    if is_blacklisted is False:
        return True
    else:
        raise errors.AuthorBlacklisted

@client.event
async def on_invite_create(invite):
    if invite.guild.id == 799330949686231050 or invite.guild.id == 882341595528175686:
        await tracker.update_invite_cache(invite)

@client.event
async def on_invite_delete(invite):
    if invite.guild.id == 799330949686231050 or invite.guild.id == 882341595528175686:
        await tracker.remove_invite_cache(invite)


# @client.event
# async def on_message(message):
#     if message.content in [f'<@!{client.user.id}>', f'<@{client.user.id}>']:
#         await message.reply(f"fuck off", mention_author=False)
#     if not message.guild: # If the message wasn't sent in a guild then:
#         return await client.process_commands(message) # Return and process the command.
#     if message.guild.id in moderated_servers:
#         if len(message.content) >  500: # If the length of the message is over 500 then:
#             await message.delete() # Deletes the message
#             warnMessage = f"Hey {message.author.mention}! Your message was over 500 characters so I had to delete it!\n*If you think this was a mistake then please contact Ender2K89 (The owner of this bot & server)*" # String that tells the author to not send messages over 500 messages
#             await message.channel.send(warnMessage, delete_after=5.0) # Sends the warnMessage and deletes it after 5 seconds
#         if message.channel.id in social_category or message.channel.id in fun_stuff_category or message.channel.id in no_mic_channel: # If the message was sent in the social, fun stuff category or the no mic channel then:
#             #url_regex = re.compile(r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')
#             #url_regex = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")
#             invite_regex = re.compile(r"<?(https?:\/\/)?(www\.)?(discord\.gg|discordapp\.com\/invite)\b([-a-zA-Z0-9/]*)>?")
#             link_perms_role = discord.utils.get(message.guild.roles, name="Link Perms")
#
#             if link_perms_role in message.author.roles:
#                 await client.process_commands(message) # Processes commands
#                 return # Return (ignore)
#             else:
#                 if invite_regex.search(message.content):
#                     await message.delete() # Deletes the message
#                     warnMessage = f"Hey {message.author.mention}! Sending discord invites is not allowed!" # String that tells the author to stop sending discord invites
#                     await message.channel.send(warnMessage, delete_after=5.0) # Sends the warnMessage and deletes it after 5 seconds
#                 else: # If it didn't match then:
#                     pass # I don't know what to put
#     await client.process_commands(message) # Processes commands

    # Commands

ready()

client.loop.run_until_complete(create_db_pool())
client.loop.create_task(run_once_when_ready())
client.run(yaml_data['TOKEN'], reconnect=True) # Runs the bot with the token being the variable "TOKEN"