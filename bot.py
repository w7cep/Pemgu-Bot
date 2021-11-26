import discord, asyncpg, os, aiohttp, pomice, openrobot.api_wrapper, random, json
from core.views import confirm, pagination
import core.utils.help as help
from discord.ext import commands

async def create_pool_postgres():
    bot.postgres = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    print("Created to the Postgres Pool")

async def get_prefix(bot, message:discord.Message):
    if not message.guild:
        return commands.when_mentioned_or(bot.default_prefix)(bot, message)
    prefix = bot.prefixes.get(message.guild.id)
    if prefix:
        return commands.when_mentioned_or(prefix)(bot, message)
    postgres = await bot.postgres.fetchval("SELECT prefix FROM prefixes WHERE guild_id=$1", message.guild.id)
    if postgres:
        prefix = bot.prefixes[message.guild.id] = postgres
    else:
        prefix = bot.prefixes[message.guild.id] = bot.default_prefix
    print(F"Cached {prefix}{'/d' if not postgres else '/p'} | {message.guild.name} - {message.guild.id}")
    return commands.when_mentioned_or(prefix)(bot, message)

async def create_session_aiohttp():
    bot.session = aiohttp.ClientSession()
    print("Created a AioHttp Session")

async def create_node_pomice():
    await bot.wait_until_ready()
    bot.pomice = pomice.NodePool()
    spotify = os.getenv("SPOTIFY").split(", ")
    await bot.pomice.create_node(bot=bot, host="lava.link", port="80", password="mom", identifier="node1lava.link", spotify_client_id=spotify[0], spotify_client_secret=spotify[1])
    await bot.pomice.create_node(bot=bot, host="node1.cjstevenson.com", port="25503", password="lookbehindyou", identifier="node1.cjstevenson.com", spotify_client_id=spotify[0], spotify_client_secret=spotify[1])
    print("Created a Pomice Node(s)")

class PemguBase(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prefixes = {}
        self.default_prefix = ".m"
        self.afks = {}
        self._commands = []
        for command in sorted(os.listdir("./core/commands/")):
            if command.endswith(".py"):
                self.load_extension(F"core.commands.{command[:-3]}")
                self._commands.append(command[:-3])
        self._events = []
        for event in sorted(os.listdir("./core/events/")):
            if event.endswith(".py"):
                self.load_extension(F"core.events.{event[:-3]}")
                self._events.append(event[:-3])
        self._others = ["Jishaku"]
        self.load_extension("jishaku")
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
        os.environ["GIT_DISCOVERY_ACROSS_FILESYSTEM"] = "True"
        self.get_command("jsk").hidden = True

    async def close(self):
        if not self.session.closed:
            await self.session.close()
        await super().close()

    @property
    def color(self):
        colors = [
            0x224585, 0x1D4E9A, 0x4879CE, 0x142966, 0x093C84,
            discord.Color.random()
        ]
        color = random.choice(colors)
        return color

    @property
    def music_color(self):
        colors = [0xFF0000, 0x1DB954, 0xFA243C, 0x159FBE, 0xFF5500, 0xFFFF64]
        color = random.choice(colors)
        return color

    async def confirm(self, ctx):
        return await confirm.ViewConfirm(ctx)

    async def pagination(self, ctx, pages):
        return await pagination.ViewPagination(ctx, pages).start()

    def trim(self, text: str, limit: int):
        text = text.strip()
        if len(text) > limit: return text[:limit-3] + "..."
        return text

bot = PemguBase(
    slash_commands=True,
    command_prefix=get_prefix,
    strip_after_prefix=True,
    case_insensitive=True,
    help_command=help.CustomHelp(),
    intents=discord.Intents.all(),
    allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False, replied_user=True)
)

@bot.check
async def blacklisted(ctx:commands.Context):
    reason = await bot.postgres.fetchval("SELECT reason FROM blacklist WHERE user_id=$1", ctx.author.id)
    if not reason: return True
    raise commands.CheckFailure(message=F"You are blacklisted: {reason}")

bot.openrobot = openrobot.api_wrapper.AsyncClient(token=os.getenv("OPENROBOT"))

bot.loop.run_until_complete(create_pool_postgres())
bot.loop.create_task(create_session_aiohttp())
bot.loop.create_task(create_node_pomice())
bot.run(os.getenv("TOKEN"))
