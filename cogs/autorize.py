from typing import Any, Dict, cast, TYPE_CHECKING
import aiohttp

import disnake
from disnake.ext import commands

from bot import BotException

if TYPE_CHECKING:
    from bot import FTKBot

ENDPOINT = 'https://ftk-sut.ru/api/discord/invite?user={0}&signature={1}'

class AutorizeError(BotException):
    def __init__(self, message) -> None:
        super().__init__(f'Ошибка авторизации: {message}')

class Autorize(commands.Cog, name='Авторизация'):
    def __init__(self, bot):
        self.bot = bot  # type: FTKBot
    
    async def process_autorization(self, user_id: int, signature: str) -> Dict[str, Any]:
        ...
    
    @commands.slash_command()
    async def autorize(*_):
        pass
    
    @autorize.sub_command()
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
            raise AutorizeError(f'ID "{user_id}" не является числом')
        user_id = int(user_id)

        if len(signature) != 64:
            raise AutorizeError(f'Подпись недействительна')

        async with self.bot.http_session.get(ENDPOINT.format(user_id, signature)) as resp:
            if resp.status != 200:
                raise AutorizeError(resp.reason)
            data = await resp.json(encoding='utf-8')
        
        future_roles = inter.user.roles
        if data['is_teacher']:
            future_roles.append(disnake.Object(764460025908690944))
        else:
            future_roles.append(disnake.Object(708966006189719562))
        if data['is_admin']:
            future_roles.append(disnake.Object(706868671196168242))

        await inter.user.edit(
            nick=data['name'],
            roles=future_roles
        )
        await inter.response.send_message(f'Вы были авторизованы как {data["name"]}')


def setup(bot):
    bot.add_cog(Autorize(bot))
