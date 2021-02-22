from discord.ext.commands import Cog, command
from apscheduler.triggers.cron import CronTrigger
from discord import Activity, ActivityType


class Meta(Cog):
    def __init__(self, bot):
        self.bot = bot

        self._message = "watching {prefix}help | {users:,} users in {guilds:,} Guilds! | Version {version}"

        bot.scheduler.add_job(self.set, CronTrigger(second=0))

    @property
    def message(self):
        return self._message.format(prefix=self.bot.config['prefix'], users=len(self.bot.users)-1, guilds=len(self.bot.guilds), version=self.bot.VERSION)

    async def set(self):
        _type, _name = self.message.split(" ", maxsplit=1)
        await self.bot.change_presence(activity=Activity(
            name=_name,
            type=getattr(ActivityType, _type, ActivityType.playing)
        ))

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('meta')


def setup(bot):
    bot.add_cog(Meta(bot))
