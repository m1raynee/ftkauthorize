from bot import FTKBot
import os

if 'DISCORD_TOKEN' in os.environ:
    from dotenv import load_dotenv
    load_dotenv()

FTKBot().run(os.environ['DISCORD_TOKEN'])
