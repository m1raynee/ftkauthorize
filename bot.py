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

exts = (
    'cogs.authorize',
)

class FTKBot(commands.Bot):
    def __init__(self):
        super().__init__(commands.when_mentioned_or('?'), test_guilds=APP_COMMAND_GUILDS)

        self.http_session = aiohttp.ClientSession(loop=self.loop)

        for ext in exts:
            try:
                self.load_extension(ext)
            except Exception as e:
                print(f'Could not load extension {ext} due to {e.__class__.__name__}: {e}')
    
    async def on_ready(self):
        print(f'Logged as: {self.user} (ID: {self.user.id})')
    
    async def on_slash_command_error(self, interaction: disnake.ApplicationCommandInteraction, exception: commands.CommandError) -> None:
        if interaction.response.is_done():
            m = interaction.followup.send
        else:
            m = interaction.response.send_message

        if isinstance(exception, BotException):
            return await m(exception.message, ephemeral=True)

        elif not interaction.application_command.has_error_handler() or interaction.application_command.cog.has_slash_error_handler():
            now = disnake.utils.utcnow().timestamp()
            content = f'Произошла непредвиденная ошибка, свяжитесь с администратором и предоставьте код {now}'
            await m(content, ephemeral=True)
            tb = '\n'.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            await self.owner.send((
                '```py\n'
                f'{interaction.user = }\n'
                f'{interaction.channel.id = }\n'
                f'{interaction.application_command.name = }\n'
                f'{interaction.options = }\n'
                '```'
            ))
            await self.owner.send(**(await safe_send_prepare(f'```py\n{tb}\n```')))

        else:
            return await super().on_slash_command_error(interaction, exception)

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        await self.owner.send((
                '```py\n'
                f'{event_method = }\n'
                f'{args = }\n'
                f'{kwargs = }\n'
                '```'
            ))
        tb = traceback.format_exc()
        await self.owner.send(**(await safe_send_prepare(f'```py\n{tb}\n```')))
