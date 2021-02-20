# modules
from asyncio.tasks import sleep
from glob import glob

from discord.ext.commands.errors import CommandOnCooldown, MissingRequiredArgument
from ..db import db
from discord import Intents
from discord.ext.commands import Bot as BotBase
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Embed
import yaml
from datetime import datetime
from pytz import timezone
from discord.ext.commands import CommandNotFound

now_utc = datetime.now(timezone('UTC'))


with open(r"./config.yaml") as file:
    config = yaml.load(file, yaml.SafeLoader)


now_time = now_utc.astimezone(timezone(config['timezone']))

# definitions
PREFIX = config['prefix']
OWNER_IDS = config['ownerids']
COGS = [path.split("\\")[-1][:-3] for path in glob('./lib/cogs/*.py')]


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
        self.PREFIX = PREFIX
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
        super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS, intents=intents)

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
            if exc == 'member is a required argument that is missing.':
                await ctx.send(f'You are Missing Required infomation! !<command> <member>')

            else:
                await ctx.send(f'You are Missing Required infomation!')

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
                timestamp=now_time
            )
            embed.set_author(
                name=f"{self.user.display_name}#{self.user.discriminator}", icon_url=f"{self.user.avatar_url}")
            embed.set_thumbnail(url=f'{self.SUP.icon_url}')
            await channel.send(embed=embed)
            self.ready = True

            print(f'Bot is Ready! On Version {self.VERSION}')
        else:
            print('Bot Reconnected!')
            channel = self.SUP.get_channel(config['startchannel'])
            await channel.send("I have Reconnected!")

    async def on_message(self, message):
        if not message.author.bot:
            now_utc = datetime.now(timezone('UTC'))
            self.time = now_utc.astimezone(timezone(config['timezone']))
            await self.process_commands(message)


bot = Bot()
