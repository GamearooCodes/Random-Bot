# modules
from discord import Intents
from discord.ext.commands import Bot as BotBase
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Embed
import yaml
from datetime import datetime
from pytz import timezone

now_utc = datetime.now(timezone('UTC'))


with open(r"./config.yaml") as file:
    config = yaml.load(file, yaml.SafeLoader)


now_time = now_utc.astimezone(timezone(config['timezone']))

# definitions
PREFIX = config['prefix']
OWNER_IDS = config['ownerids']

# start of bot


class Bot(BotBase):
    def __init__(self):
        # self definitions
        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None
        self.SUP = None
        self.scheduler = AsyncIOScheduler()
        self.config = config

        intents = Intents.default()
        intents.members = True

        # *Start of main bot code
        super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS, intents=intents)

    def run(self, VERSION):
        self.VERSION = VERSION

        self.TOKEN = config['token']

        print("Running Bot...")
        super().run(self.TOKEN, reconnect=True)

    async def on_connect(self):
        print("Bot is Ready!")

    async def on_disconnect(self):
        print('Bot Lost Internet Connection!')

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.SUP = self.get_guild(config['support-server'])
            channel = self.SUP.get_channel(config['startchannel'])

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

            print(f'Bot Ready! On Version {self.VERSION}')
        else:
            print('Bot Reconnected!')
            channel = self.SUP.get_channel(config['startchannel'])
            await channel.send("I have Reconnected!")

    async def on_message(self, message):
        pass


bot = Bot()
