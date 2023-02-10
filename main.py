import asyncio
import logging
import os
import sys

import discord
from dotenv import load_dotenv

from objects.bot import Val
from objects.command_tree import CommandTree
from objects.discord_changes import Embed, View

if not os.path.exists("logs"):
    os.mkdir("logs")

load_dotenv(".env")


"""_summary_
This will be the static logging for discord.
"""
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.WARNING)
formatter = logging.Formatter("\x1b[38;5;203m[%(levelname)s: %(name)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
handler = logging.FileHandler(filename="logs/discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)

bot = Val(intents=discord.Intents.all(), owner_id=723386696007155763, tree_cls=CommandTree)
discord.Embed = Embed
discord.Embed.bot = bot
discord.ui.View = View



if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        loop.set_debug(True)
        asyncio.set_event_loop(loop)

        loop.create_task(bot.start(os.getenv("TOKEN")))
        loop.run_forever()

    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
         bot.logger.critical("Fucking off...")

    finally:
        loop.close()
        bot.logger.critical("Bot fucked off....")
        sys.exit()
