# modules
from asyncio.tasks import sleep
from glob import glob

from discord.ext.commands.errors import CommandOnCooldown, MissingRequiredArgument, MissingPermissions, BotMissingPermissions
from ..db import db
from discord import Intents
from discord.ext.commands import Bot as BotBase
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Embed
import yaml
from datetime import datetime
import pytz
from discord.ext.commands import CommandNotFound, when_mentioned_or


now_utc = datetime.now(pytz.timezone('America/New_York'))
now = datetime.now(pytz.timezone('America/New_York'))


with open(r"./config.yaml") as file:
    config = yaml.load(file, yaml.SafeLoader)


# new_t = now.astimezone(timezone)

new_timezone_object = pytz.timezone(config['timezone'])
new_t = now.astimezone(new_timezone_object)

os = config['os']
if(os == 'windows'):
    type = '\\'

if(os == 'linux'):
    type = '\\'

if(os == 'mac'):
    type = ':'  # ! if this is wrong plz dm me to have this Directory Separator fixed! Gamearoo#0001

if(os == 'windows'):
    print('Loaded On Windows!')

if(os == 'linux'):
    print('Loaded On Linux!')

if(os == 'mac'):
    print('Loaded On Mac (Not fully Supported!)')

# definitions
PREFIX = config['prefix']
OWNER_IDS = config['ownerids']
COGS = [path.split(type)[-1][:-3] for path in glob('./lib/cogs/*.py')]


def get_prefix(bot, message):

    prefix = db.field(
        "SELECT prefix FROM Guilds WHERE guildId = ?", message.guild.id)
    if not prefix:
        prefix = config['prefix']

        db.execute(
            'INSERT INTO Guilds (guildId, guildName, prefix) VALUES(?,?,?)', message.guild.id, message.guild.name, PREFIX)

    return when_mentioned_or(prefix)(bot, message)


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)
            print(f'Loading {cog}...')

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f'{cog} cog Ready!')

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])

# start of bot


class Bot(BotBase):
    def __init__(self):
        # self definitions
        self.os = config['os']

        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.SUP = None
        self.scheduler = AsyncIOScheduler()
        self.config = config

        db.autosave(self.scheduler)

        intents = Intents.default()
        intents.members = True

        # *Start of main bot code
        super().__init__(command_prefix=get_prefix,
                         owner_ids=OWNER_IDS, intents=Intents.all())

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")
        print('Setup Completed!')

    def run(self, VERSION):
        self.VERSION = VERSION

        print("Running Setup....")
        self.setup()

        self.TOKEN = config['token']

        print("Running Bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):

        print("Bot connected!")

    async def on_disconnect(self):
        print('Bot Lost Internet Connection!')

    async def on_error(self, err, *args, **kwargs):
        if err == 'on_command_error':
            await args[0].send("Something Went Wrong.")

        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f'That command is on {str(exc.cooldown.type).split(".")[-1]} Cooldown. Try again in {exc.retry_after:,.2f} secs.')

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send(f'You are Missing Required infomation!')

        elif isinstance(exc, MissingPermissions):
            await ctx.send(f"{ctx.author.mention}, {exc}")
        elif isinstance(exc, BotMissingPermissions):
            await ctx.send(f"{ctx.author.mention}, {exc}")

        elif hasattr(exc, "original"):
            raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:

            self.SUP = self.get_guild(config['support-server'])

            self.scheduler.start()
            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            channel = self.SUP.get_channel(config['botlog'])

            embed = Embed(
                title="Now Online!",
                description=f'{self.user.mention} Is Online!',
                color=0x00FF00,
                timestamp=new_t
            )
            embed.set_author(
                name=f"{self.user.display_name}#{self.user.discriminator}", icon_url=f"{self.user.avatar_url}")
            embed.set_thumbnail(url=f'{self.SUP.icon_url}')
            await channel.send(embed=embed)
            self.ready = True

            print(f'Bot is Ready! On Version {self.VERSION}')

            meta = self.get_cog('Meta')
            await meta.set()
        else:
            print('Bot Reconnected!')
            channel = self.SUP.get_channel(config['startchannel'])
            await channel.send("I have Reconnected!")

    async def on_message(self, message):
        if not message.author.bot:
            for channel in message.guild.channels:
                if channel.name == config['modlog']:

                    cid = channel.id

                elif message.guild.id == config['support-server']:
                    cid = config['support-server-modlogs']

                else:
                    cid = config['modlog']

                self.modlog = self.get_channel(cid)

            for role in message.guild.roles:
                if role.name == config['muterole']:

                    rid = role.id

                elif message.guild.id == config['support-server']:
                    rid = config['support-server-muterole']

                else:
                    rid = config['muterole']

                self.muterole = message.guild.get_role(rid)

            argerr = Embed(
                title="Error",
                description=f'You are Missing Required infomation!',
                color=0xFF0000,
                timestamp=new_t
            )
            self.argerr = argerr
            db.execute(
                "UPDATE Guilds SET guildName = ? WHERE guildId = ?", message.guild.name, message.guild.id)
            now_utc = datetime.now(pytz.timezone('UTC'))
            self.time = now_utc.astimezone(pytz.timezone(config['timezone']))
            prefix = db.field(
                "SELECT prefix FROM Guilds WHERE guildId = ?", message.guild.id)
            self.PREFIX = prefix
            await self.process_commands(message)


bot = Bot()
