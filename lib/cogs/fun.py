from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Member, Embed
from typing import Optional
from random import choice, randint


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="hello", aliases=['hi'])
    async def hello(self, ctx):
        msg = choice(('Hello', 'Hello, How are you today?', 'Hi'))
        await ctx.channel.send(f"{msg} {ctx.author.mention}!")

    @command(name='dice')
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d"))
        rolls = [randint(1, value) for i in range(dice)]

        await ctx.channel.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

    @command(name='slap', aliases=['hit'])
    async def slapping(self, ctx, member: Member, *, reason: str = "For No Reason"):
        image = choice(('https://gamearoo.top/wp-content/uploads/2020/04/slap.gif', 'https://gamearoo.top/wp-content/uploads/2020/04/slap2.gif',
                        'https://gamearoo.top/wp-content/uploads/2020/04/slap3.gif', 'https://gamearoo.top/wp-content/uploads/2020/04/slap4.gif'))
        embed = Embed(
            description=f'{ctx.author.mention} Slapped {member.mention} {reason}',
            color=0xF90000,
            timestamp=self.bot.time
        )
        embed.set_author(
            name=f"{ctx.author.display_name}#{ctx.author.discriminator}", icon_url=f"{ctx.author.avatar_url}")
        embed.set_thumbnail(url=f'{member.avatar_url}')
        embed.set_image(url=f'{image}')

        await ctx.channel.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
