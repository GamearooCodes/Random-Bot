from discord.ext.commands import Cog, command

from ..db import db


class Bye(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('bye')

    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute("DELETE FROM exp WHERE UserID = ?", member.id)
        for channel in member.guild.channels:
            if channel.name == self.bot.config['bye']:
                cid = channel.id

        await self.bot.get_channel(cid).send(f"**{member}** has left **{member.guild.name}**!")


def setup(bot):
    bot.add_cog(Bye(bot))
