import discord, asyncpg, os, aiohttp, pomice, openrobot.api_wrapper, random
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
    print(F"Cached {F'{prefix}/d' if not postgres else F'{postgres}/p'} | {message.guild.name} - {message.guild.id}")
    return commands.when_mentioned_or(prefix)(bot, message)

async def create_session_aiohttp():
    bot.session = aiohttp.ClientSession()
    print("Created a AioHttp Session")

async def create_node_pomice():
    await bot.wait_until_ready()
    lnodes = [
        "lavalink.darrennathanael.com",
        "lava.link"
    ]
    dnodes = {
        "lavalink.darrennathanael.com": {"port": "80", "pw": "clover", "identifier": "clover"},
        "lava.link": {"port": "80", "pw": "math", "identifier": "math"}
    }
    slnodes = [
        "lavalink.cjstevenson.xyz",
        "lavalink.cjstevenson.com",
        "lavalink.devz.cloud",
        "lavalink2.devz.cloud",
        "disbotlistlavalink.ml",
        "lavalink.mrpriyamyt.repl.co"
    ]
    sdnodes = {
        "lavalink.cjstevenson.xyz": {"pw": "lookbehindyou", "identifier": "lookbehindyou"},
        "lavalink.cjstevenson.com": {"pw": "lookbehindyou", "identifier": "lookbehindyou"},
        "lavalink.devz.cloud": {"pw": "mathiscool", "identifier": "mathiscool"},
        "lavalink2.devz.cloud": {"pw": "mathiscool", "identifier": "mathiscool"},
        "disbotlistlavalink.ml": {"pw": "LAVA", "identifier": "LAVA"},
        "lavalink.mrpriyamyt.repl.co": {"pw": "methisbigbrain", "identifier": "methisbigbrain"}
    }
    bot.pomice = pomice.NodePool()
    for n in lnodes:
        await bot.pomice.create_node(bot=bot, host=n, port=dnodes.get(n)["port"], password=dnodes.get(n)["pw"], identifier=dnodes.get(n)["identifier"], spotify_client_id=os.getenv("SPOTIFY").split(", ")[0], spotify_client_secret=os.getenv("SPOTIFY").split(", ")[1])
        print(F"Created a Pomice Node: {n} - {dnodes.get(n)['identifier']}")
    for s in slnodes:
        await bot.pomice.create_node(bot=bot, secure=True, host=s, port=443, password=sdnodes.get(s)["pw"], identifier=sdnodes.get(s)["identifier"], spotify_client_id=os.getenv("SPOTIFY").split(", ")[0], spotify_client_secret=os.getenv("SPOTIFY").split(", ")[1])
        print(F"Created a Secure Pomice Node: {s} - {sdnodes.get(s)['identifier']")

class PemguBase(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prefixes = {}
        self.default_prefix = ".m"
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
        self.afks = {}

    async def close(self):
        if not self.session.closed:
            await self.session.close()
        await super().close()

    @property
    def color(self):
        colors = [
            0x224585, 0x1D4E9A, 0x4879CE, 0x142966, 0x093C84,
            discord.Color.blue(),
            discord.Color.blurple(),
            discord.Color.brand_green(),
            discord.Color.brand_red(),
            discord.Color.dark_blue(),
            discord.Color.dark_gold(),
            discord.Color.dark_gray(),
            discord.Color.dark_green(),
            discord.Color.dark_grey(),
            discord.Color.dark_magenta(),
            discord.Color.dark_orange(),
            discord.Color.dark_purple(),
            discord.Color.dark_red(),
            discord.Color.dark_teal(),
            discord.Color.dark_theme(),
            discord.Color.darker_gray(),
            discord.Color.darker_grey(),
            discord.Color.default(),
            discord.Color.fuchsia(),
            discord.Color.gold(),
            discord.Color.green(),
            discord.Color.greyple(),
            discord.Color.light_gray(),
            discord.Color.light_grey(),
            discord.Color.lighter_gray(),
            discord.Color.lighter_grey(),
            discord.Color.magenta(),
            discord.Color.og_blurple(),
            discord.Color.orange(),
            discord.Color.purple(),
            discord.Color.random(),
            discord.Color.red(),
            discord.Color.teal(),
            discord.Color.yellow()
        ]
        color = random.choice(colors)
        return color

    @classmethod
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
    allowed_mentions=discord.AllowedMentions.none()
)

@bot.command(name="news", aliases=["new"])
async def news(ctx:commands.Context):
    message = await bot.http.get_message(898287740267937813, 908136879944253490)
    newmbed = discord.Embed(
        color=bot.color,
        title="Latest News",
        description=message.get("content"),
        timestamp=ctx.message.created_at
    )
    newmbed.set_footer(text=ctx.author, icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=newmbed)

@bot.check
async def blacklisted(ctx:commands.Context):
    reason = await bot.postgres.fetchval("SELECT reason FROM blacklist WHERE user_id=$1", ctx.author.id)
    if not reason: return True
    raise commands.CheckFailure(message=F"You are blacklisted: {reason}")

bot.openrobot = openrobot.api_wrapper.AsyncClient(token=os.getenv("OPENROBOT"))

bot.loop.run_until_complete(create_pool_postgres())
bot.loop.run_until_complete(create_session_aiohttp())
bot.loop.create_task(create_node_pomice())
bot.run(os.getenv("TOKEN"))
