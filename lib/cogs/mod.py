from discord.ext.commands import Cog, BucketType, Greedy
from discord.ext.commands import command, cooldown, CheckFailure, has_permissions, bot_has_permissions
from discord import Member, Embed
from typing import Optional
from random import choice, randint
from aiohttp import request
from datetime import datetime, timedelta
from asyncio.tasks import sleep

from ..db import db


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='kick', help='Kick a member out of the server!', brief='Kick a member!')
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)
    async def kick(self, ctx, targets: Greedy[Member], *, reason: str = 'No Reason Provided!'):
        if not len(targets):
            await ctx.send(embed=self.bot.argerr)

        else:
            for target in targets:
                await target.kick(reason=reason)

                embed = Embed(
                    title="Member Kicked!",
                    color=0xFF0000,
                    timestamp=self.bot.time
                )
                embed.set_thumbnail(url=target.avatar_url)
                fields = [("Member", target.display_name, False),
                          ("Kicked By",
                           f"{ctx.author.mention} ({ctx.author})", False),
                          ("Reason", reason, False)]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.bot.modlog.send(embed=embed)

    @command(name='ban', help='Ban a member out of the server!', brief='Ban a member!')
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)
    async def ban(self, ctx, targets: Greedy[Member], *, reason: str = 'No Reason Provided!'):
        if not len(targets):
            await ctx.send(embed=self.bot.argerr)

        else:
            for target in targets:
                await target.ban(reason=reason)

                embed = Embed(
                    title="Member Banned!",
                    color=0xFF0000,
                    timestamp=self.bot.time
                )
                embed.set_thumbnail(url=target.avatar_url)
                fields = [("Member", target.display_name, False),
                          ("Banned By",
                           f"{ctx.author.mention} ({ctx.author})", False),
                          ("Reason", reason, False)]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)

                await self.bot.modlog.send(embed=embed)

    @command(name='clear', help='Clear bulk messages!', brief='clear muti msges!', aliases=['prune', 'purge'])
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear(self, ctx, targets: Greedy[Member], limit: int):
        def _check(message):
            return not len(targets) or message.author in targets

        if 0 < limit <= 100:
            with ctx.channel.typing():
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit, after=datetime.utcnow()-timedelta(days=14), check=_check)

                await ctx.send(f"Deleted {len(deleted):,} messages.", delete_after=5)

        else:
            await ctx.send(f"The number provided must be less then 100", delete_after=5)

    @command(name='mute', help='Mutes a member or members!', brief='mute members!')
    @bot_has_permissions(manage_roles=True, manage_messages=True)
    @has_permissions(manage_roles=True, manage_messages=True)
    async def mute(self, ctx, targets: Greedy[Member], seconds: Optional[int], *, reason: Optional[str] = "No reason Provided"):
        if not len(targets):
            await ctx.send(embed=self.bot.argerr)
        else:
            unmutes = []

            for target in targets:
                if not self.bot.muterole in target.roles:
                    if ctx.guild.me.top_role.position > target.top_role.position:
                        role_ids = ",".join([str(r.id) for r in target.roles])
                        end_time = datetime.utcnow() + timedelta(seconds=seconds) if seconds else None

                        db.execute("INSERT INTO mutes (UserID, Username, RolesIDs, EndTime, muteroleid) VALUES (?,?,?,?,?)", target.id,
                                   target.display_name, role_ids, getattr(end_time, "isoformat", lambda: None)(), self.bot.muterole.id)

                        await target.edit(roles=[self.bot.muterole])

                        embed = Embed(
                            title="Member Muted!",
                            color=target.color,
                            timestamp=self.bot.time
                        )
                        embed.set_thumbnail(url=target.avatar_url)

                        fields = [("Member", target.display_name, False),
                                  ("Muted By",
                                   f"{ctx.author.mention} ({ctx.author})", False),
                                  ("Duration",
                                   f"{seconds:,} second(s)" if seconds else "Lifetime", False),
                                  ("Reason", reason, False)]

                        for name, value, inline in fields:
                            embed.add_field(
                                name=name, value=value, inline=inline)
                        await self.bot.modlog.send(embed=embed)
                        if seconds:
                            unmutes.append(target)
                    else:
                        await ctx.reply(f"I Can\'t Mute {target.metion}. There Higher Or Equal To Me.")
                else:
                    await ctx.send(f"{target.metion} is already Muted!")
            await ctx.send('Action Completed!')

            if len(unmutes):
                await sleep(seconds)
                await self.unmute(ctx, targets, self.bot.muterole, self.bot.user)

    async def unmute(self, ctx, targets, muterole, member, *,  reason="Mute time expired."):

        for target in targets:
            if muterole in target.roles:
                role_ids = db.field(
                    "SELECT RolesIDs FROM mutes WHERE UserID = ?", target.id)
                roles = [ctx.guild.get_role(int(id_))
                         for id_ in role_ids.split(",") if len(id_)]

                db.execute("DELETE FROM mutes WHERE UserID = ?", target.id)

                await target.edit(roles=roles)

                embed = Embed(
                    title="Member UnMuted!",
                    color=target.color,
                    timestamp=self.bot.time
                )
                embed.set_thumbnail(url=target.avatar_url)

                fields = [("Member", target.display_name, False),
                          ("UnMuted By",
                              f"{member.mention} ({member})", False),
                          ("Reason", reason, False)]

                for name, value, inline in fields:
                    embed.add_field(
                        name=name, value=value, inline=inline)
                await self.bot.modlog.send(embed=embed)

    @command(name='unmute', help='unMutes a member or members!', brief='unmute members!')
    @bot_has_permissions(manage_roles=True, manage_messages=True)
    @has_permissions(manage_roles=True, manage_messages=True)
    async def unmute_member(self, ctx, targets: Greedy[Member], *, reason: Optional[str] = "No reason Provided"):
        if not len(targets):
            await ctx.send(embed=self.bot.argerr)
        else:
            await self.unmute(ctx, targets, self.bot.muterole, ctx.author,  reason=reason)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:

            self.bot.cogs_ready.ready_up('mod')


def setup(bot):
    bot.add_cog(Mod(bot))
