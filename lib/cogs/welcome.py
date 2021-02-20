from discord.ext.commands import Cog, command


from ..db import db


class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('welcome')

    @Cog.listener()
    async def on_member_join(self, member):
        db.execute(
            'INSERT INTO exp(UserID, Username) VALUES (?, ?)', member.id, member.display_name)

        if not self.bot.config['welcome']:
            pass

        for channel in member.guild.channels:
            if channel.name == self.bot.config['welcome']:

                cid = channel.id

        await self.bot.get_channel(cid).send(f"Welcome **{member.mention}** to **{member.guild.name}**!")


def setup(bot):
    bot.add_cog(Welcome(bot))
