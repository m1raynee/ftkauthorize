import re
from typing import TYPE_CHECKING
import aiohttp

import disnake
from disnake.ext import commands

from bot import BotException
from .utils.views import Linked

if TYPE_CHECKING:
    from bot import FTKBot

ENDPOINT = 'https://ftk-sut.ru/api/discord/invite?user={0}&signature={1}'
AUTHORIZATION_CHANNEL_ID = 777259995334311966
SIGNATURE_REGEX = re.compile(r'[a-z0-9]{64}')


class AuthorizeError(BotException):
    def __init__(self, message) -> None:
        super().__init__(f'Ошибка авторизации: {message}')

class Authorize(commands.Cog, name='Авторизация'):
    def __init__(self, bot):
        self.bot = bot  # type: FTKBot
    
    @commands.slash_command()
    async def authorize(*_):
        pass
    
    @authorize.sub_command()
    async def process(
        self,
        inter: disnake.ApplicationCommandInteraction,
        code: str
    ):
        """
        Авторизация

        Parameters
        ----------
        code: Код для авторизации. Информация: /autorize info
        """
        user_id, signature = code.split('.', 1)

        if not user_id.isdigit():
            raise AuthorizeError(f'ID "{user_id}" не является числом')
        user_id = int(user_id)

        match = re.match(SIGNATURE_REGEX, signature)

        if not match:
            raise AuthorizeError(f'Подпись недействительна')
        signature = match.group(0)

        async with self.bot.http_session.get(ENDPOINT.format(user_id, signature)) as resp:
            if resp.status != 200:
                raise AuthorizeError(resp.reason)
            data = await resp.json(encoding='utf-8')
        
        future_roles = inter.user.roles
        if data['is_teacher']:
            future_roles.append(disnake.Object(764460025908690944))
        else:
            future_roles.append(disnake.Object(708966006189719562))

        await inter.user.edit(
            nick=data['name'],
            roles=future_roles
        )
        await inter.response.send_message(f'Вы были авторизованы как {data["name"]}')
        try:
            await inter.author.send(f'Вы были авторизованы как {data["name"]}')
        except: pass

    @authorize.sub_command()
    async def info(self, inter: disnake.ApplicationCommandInteraction):
        """Информация об авторизации"""
        view = Linked(
            'https://discord.com/channels/705650591006982235/777259995334311966/897917001408864286',
            'Перейти к инструкции'
        )
        await inter.response.send_message('Информационное сообщение', view=view, ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        view = Linked(
            'https://discord.com/channels/705650591006982235/777259995334311966/897917001408864286',
            'Перейти к инструкции'
        )
        try:
            await member.send('Пройдите авторизацию на сервере', view=view)
        except:
            dest = self.bot.get_partial_messageable(AUTHORIZATION_CHANNEL_ID)
            await dest.send('Пройдите авторизацию на сервере', view=view)


def setup(bot):
    bot.add_cog(Authorize(bot))
