import json
import discord
import requests
from discord import Embed, Color
from discord.ext import commands
from conf import url, channels
from init import Roles
future_roles = []


class Authorize(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def authorize(self, message):
        roles = Roles(message.guild)
        codes = message.content.split('.')
        if len(codes) == 3:
            response = requests.get(
                f'{url}/discord/invite?expires={codes[0]}&user={codes[1]}&signature={codes[2]}'
            )
            if response.status_code == 200:
                content = json.loads(response.content.decode('utf8').replace("'", '"'))

                if content['is_admin']:
                    future_roles.append(roles.admin)
                    if content['is_teacher']:
                        future_roles.append(roles.teacher)
                    else:
                        future_roles.append(roles.pupil)
                else:
                    if content['is_teacher']:
                        future_roles.append(roles.teacher)
                    else:
                        future_roles.append(roles.pupil)
                
                await message.author.edit(
                    nick=content['name'],
                    roles=future_roles
                )
                await message.author.send(embed=Embed(
                    title=None,
                    colour=Color.dark_theme()
                ).add_field(
                    name=f'Вы авторизовались на сервере ФТК СЮТ',
                    value=f'Теперь вы {content["name"]}'
                ))
                return
        await message.author.send(embed=Embed(
            title=None,
            colour=Color.dark_theme()
        ).add_field(
            name=f'Вы пытались авторизоваться на сервере ФТК СЮТ',
            value=f'К сожалению, введённый вами код неверен'
        ))


    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.edit(
            roles = [
                Roles(member.guild).undefined
            ]
        )
        await member.send('Отправьте код авторизации сюда. Получить код: https://ftk-sut.ru/home')

        msg = await self.bot.wait_for('message')
        await self.authorize(msg)


    @commands.command(name='auth', aliases = ['авторизовать', 'авторизация'])
    async def auth_command(self, ctx):
        if type(ctx.channel) != discord.DMChannel:
            return await ctx.send('Команда работет только в ЛС бота.')

        await ctx.author.send('Отправьте код авторизации сюда. Получить код: https://ftk-sut.ru/home')
        msg = await self.bot.wait_for('message')
        await self.authorize(msg)


def setup(bot):
    bot.add_cog(Authorize(bot))
    print('Extension "Authorize" loaded')

def teardown(bot):
    bot.remove_cog(Authorize(bot))
    print('Extension "Authorize" unloaded')