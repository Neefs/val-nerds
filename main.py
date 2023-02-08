import asyncio
import discord

from discord.ext import commands
from utils.bot import PlaceHolder
import json

with open("config.json", "r") as readfile:
    config = json.loads(readfile.read())


async def main():
    bot = PlaceHolder(config=config, intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        print(f"{bot.name} bot is ready.")

    await bot.starting_logic()
    try:
        await bot.start(config["bot"]["token"])
    except (KeyboardInterrupt, SystemExit):
        print("\n\nBot has been stopped\n\n")
    finally:
        await bot.closing_logic()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    print("\n\nBot has been stopped\n\n")
