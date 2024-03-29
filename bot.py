import traceback

import aiohttp
import disnake
from disnake.ext import commands

from cogs.utils import safe_send_prepare


class BotException(Exception):
    def __init__(self, message) -> None:
        self.message = message


APP_COMMAND_GUILDS = (
    705650591006982235,
)

init_exts = (
    'cogs.authorize',
    'jishaku'
)

class FTKBot(commands.Bot):
    def __init__(self):
        super().__init__(
            commands.when_mentioned_or('?'),
            test_guilds=APP_COMMAND_GUILDS,
            intents=disnake.Intents.all()
        )
        self.call_once = True

        self.http_session = aiohttp.ClientSession(loop=self.loop)

        for ext in init_exts:
            try:
                self.load_extension(ext)
            except Exception as e:
                t = traceback.format_exception(None, e, e.__traceback__)
                print(f'Could not load extension {ext} due to {e.__class__.__name__}: {e}\n{"".join(t)}')
    
    async def on_ready(self):
        print(f'Logged as: {self.user} (ID: {self.user.id})')

        if self.call_once:
            self.error_log = await self.fetch_user(428483942329614336)
            self.call_once = False
    
    async def on_slash_command_error(self, interaction: disnake.ApplicationCommandInteraction, exception: commands.CommandError) -> None:
        if isinstance(exception, BotException):
            return await interaction.send(exception.message, ephemeral=True)

        now = disnake.utils.utcnow().timestamp()
        content = f'Произошла непредвиденная ошибка, свяжитесь с администратором и предоставьте код {now}'
        await interaction.send(content, ephemeral=True)
        tb = '\n'.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        await self.error_log.send((
            '```py\n'
            f'{interaction.user = }\n'
            f'{interaction.channel_id = }\n'
            f'{interaction.application_command.name = }\n'
            f'{interaction.options = }\n'
            '```'
        ))
        await self.error_log.send(**safe_send_prepare(f'```py\n{tb}\n```'))


    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        await self.error_log.send((
            '```py\n'
            f'{event_method = }\n'
            f'{args = }\n'
            f'{kwargs = }\n'
            '```'
        ))
        tb = traceback.format_exc()
        await self.error_log.send(**safe_send_prepare(f'```py\n{tb}\n```'))
