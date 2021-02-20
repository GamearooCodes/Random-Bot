from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown, has_permissions
from discord import Member, Embed
from typing import Optional
from random import choice, randint
from aiohttp import request

from ..db import db


class Config(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='setprefix', aliases=['prefix'], help='Set the prefix for the Guild!', brief='Set The Prefix!')
    @has_permissions(manage_guild=True)
    async def change_prefix(self, ctx, new: str):
        if len(new) > 5:
            await ctx.send("The Prefix can't be more than 5 characters in length!")

        else:
            db.execute(
                "UPDATE Guilds SET prefix = ? WHERE guildId = ?", new, ctx.guild.id)
            await ctx.send(f"Prefix set to **{new}**")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("config")


def setup(bot):
    bot.add_cog(Config(bot))
