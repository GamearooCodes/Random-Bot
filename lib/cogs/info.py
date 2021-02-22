from discord.ext.commands import Cog, command
from discord import Embed, Member
from typing import Optional


class Info(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="userinfo", aliases=['ui', "memberinfo", "mi"])
    async def user_info(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        embed = Embed(
            title="User Info",
            color=target.color,
            timestamp=self.bot.time
        )
        embed.set_thumbnail(url=target.avatar_url)
        fields = [("ID", target.id, False),
                  ("Name", str(target.display_name), True),
                  ("Bot?", target.bot, True),
                  ("Top Role", target.top_role.mention, True),
                  ("Status?", target.status, True),
                  ("Created On", target.created_at.strftime(
                      "%m/%d/%Y %H:%M:%S"), True),
                  ("Activity",
                   f"{target.activity.name if target.activity else 'N/A'}", True),
                  ("Activity Type",
                   f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'}", True),
                  ("Joined", target.joined_at.strftime("%m/%d/%Y %H:%M:%S"), True),
                  ("Boosted?", True if target.premium_since else False, True)

                  ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @command(name='serverinfo', aliases=['guildinfo', 'si', 'gi'])
    async def guild_info(self, ctx):
        embed = Embed(
            title="Server Info",
            color=ctx.guild.owner.color,
            timestamp=self.bot.time
        )
        embed.set_thumbnail(url=ctx.guild.icon_url)

        statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status)
                                    == "idle", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]

        fields = [("ID", ctx.guild.id, True),
                  ("Owner", ctx.guild.owner.mention, True),
                  ("Region", ctx.guild.region, True),
                  ("Created at", ctx.guild.created_at.strftime(
                      "%m/%d/%Y %H:%M:%S"), True),
                  ("Members", len(ctx.guild.members), True),
                  ("Humans", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
                  ("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
                  ("Banned members", len(await ctx.guild.bans()), True),
                  ("Text channels", len(ctx.guild.text_channels), True),
                  ("Statuses",
                   f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}", True),
                  ("Voice channels", len(ctx.guild.voice_channels), True),
                  ("Categories", len(ctx.guild.categories), True),
                  ("Roles", len(ctx.guild.roles), True),
                  ("Invites", len(await ctx.guild.invites()), True),
                  ("\u200b", "\u200b", True)

                  ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('info')


def setup(bot):
    bot.add_cog(Info(bot))
