import os
import discord
from discord.ext import commands

from conf import *
client = commands.Bot(command_prefix = settings['prefix'], intents = discord.Intents.all())
client.remove_command('help')


@client.event
async def on_ready():
    print(f'\nWe logged as {client.user}')


@client.command(aliases = ['extload', 'l'])
async def __load(ctx, ext = None):
    if ext:
        client.load_extension(f'commands.{ext}')
        await ctx.send(f'Расширение "{ext}" загружено')
    else:
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                client.load_extension(f'commands.{filename[:-3]}')
    
        await ctx.send('Все расширения загружены')
    


@client.command(aliases = ['extunload', 'ul'])
async def __unload(ctx, ext = None):
    if ext:
        client.unload_extension(f'commands.{ext}')
        await ctx.send(f'Расширение "{ext}" отгружено')
    else:
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                client.unload_extension(f'commands.{filename[:-3]}')
        await ctx.send('Все расширения отгружены')


@client.command(aliases = ['extreload', 'rl'])
async def __reload(ctx, ext = None):
    if ext:
        client.reload_extension(f'commands.{ext}')
        await ctx.send(f'Расширение "{ext}" перезагружено')
    else:
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                client.reload_extension(f'commands.{filename[:-3]}')
        await ctx.send('Все расширения перерагружены')


for filename in os.listdir('./commands'):
    if filename.endswith('.py'):
        client.load_extension(f'commands.{filename[:-3]}')

client.run(settings['token'])
