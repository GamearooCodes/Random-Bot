from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown
from discord import Member, Embed
from typing import Optional
from random import choice, randint
from aiohttp import request


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="hello", aliases=['hi'])
    @cooldown(1, 70, BucketType.user)
    async def hello(self, ctx):
        msg = choice(('Hello', 'Hello, How are you today?', 'Hi'))
        await ctx.channel.send(f"{msg} {ctx.author.mention}!")

    @command(name='dice')
    @cooldown(2, 10, BucketType.guild)
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d"))
        rolls = [randint(1, value) for i in range(dice)]

        await ctx.channel.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")

    @command(name='slap', aliases=['hit'])
    @cooldown(2, 60, BucketType.user)
    async def slapping(self, ctx, member: Member, *, reason: str = "For No Reason"):
        if not member:
            ctx.send('Please Metion A Member!')

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

    @command(name='dog')
    @cooldown(1, 60, BucketType.user)
    async def dog_image(self, ctx):
        URL = 'https://some-random-api.ml/img/dog'
        async with request('GET', URL, headers={}) as response:
            if response.status == 200:
                image = await response.json()

                embed = Embed(
                    description=f'Heres a random Dog {ctx.author.mention}',
                    color=0x00B9F9,
                    timestamp=self.bot.time
                )
                embed.set_author(
                    name=f"{ctx.author.display_name}#{ctx.author.discriminator}", icon_url=f"{ctx.author.avatar_url}")
                embed.set_image(url=f'{image["link"]}')

                await ctx.channel.send(embed=embed)

            else:
                await ctx.send(f'The api i use returned a {response.status} Status. :(')

    @command(name='dogfact')
    @cooldown(1, 60, BucketType.user)
    async def dog_fact(self, ctx):
        URL2 = 'https://some-random-api.ml/facts/dog'
        async with request('GET', URL2, headers={}) as response:
            if response.status == 200:
                data = await response.json()

                embed = Embed(
                    description=f'{data["fact"]}',
                    color=0x00B9F9,
                    timestamp=self.bot.time
                )
                embed.set_author(
                    name=f"{ctx.author.display_name}#{ctx.author.discriminator}", icon_url=f"{ctx.author.avatar_url}")

                await ctx.channel.send(embed=embed)

            else:
                await ctx.send(f'The api i use returned a {response.status} Status. :(')

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
