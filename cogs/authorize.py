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

class InvalidCode(BotException):
    def __init__(self) -> None:
        super().__init__('Ошибка авторизации: Неверный ключ-код')

class Authorize(commands.Cog, name='Авторизация'):
    def __init__(self, bot):
        self.bot = bot  # type: FTKBot
    
    @commands.slash_command()
    async def authorize(self, inter: disnake.ApplicationCommandInteraction, code: str):
        """Авторизация

        Parameters
        ----------
        code: Код для авторизации, который можно найти на сайте.
        """
        user_id, signature = code.split('.', 1)

        if not user_id.isdigit():
            raise InvalidCode()
        user_id = int(user_id)

        match = re.match(SIGNATURE_REGEX, signature)

        if not match:
            raise InvalidCode()
        signature = match.group(0)

        async with self.bot.http_session.get(ENDPOINT.format(user_id, signature)) as resp:
            if resp.status != 200:
                raise InvalidCode()
            data = await resp.json(encoding='utf-8')
        
        if data['is_teacher']:
            await inter.author.add_roles(disnake.Object(764460025908690944))
        else:
            await inter.author.add_roles(disnake.Object(708966006189719562))

        await inter.author.edit(nick=data['name'])
        await inter.response.send_message(f'{inter.author.name} теперь {data["name"]}')
        try:
            await inter.author.send(f'Вы были авторизованы как {data["name"]}')
        except disnake.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        view = Linked(
            'https://discord.com/channels/705650591006982235/777259995334311966/897917001408864286',
            'Перейти к инструкции'
        )
        try:
            await member.send('Пройдите авторизацию на сервере', view=view)
        except disnake.HTTPException:
            dest = self.bot.get_partial_messageable(AUTHORIZATION_CHANNEL_ID)
            await dest.send('Пройдите авторизацию на сервере', view=view)


def setup(bot):
    bot.add_cog(Authorize(bot))
