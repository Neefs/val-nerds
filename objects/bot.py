import logging
import os
from discord.ext import commands
from utils.database import Database
import discord
from objects.discord_changes import Embed
import jishaku
import aiohttp
import traceback as tb

class Val(commands.AutoShardedBot):
    def __init__(self, **options):
        self.prefix = options.get("prefix", ".")
        super().__init__(commands.when_mentioned_or(self.prefix), **options)
        self.db:Database =None
        self.session:aiohttp.ClientSession = None


        self.ignore_extensions = [
        ]
        if not os.path.exists("extensions"):
            os.mkdir("extensions")

        self.extensions_path = [
            "jishaku",
            "utils.database",
            *[
                f"extensions.{ext[:-3]}"
                for ext in os.listdir("extensions")
                if ext.endswith('.py') 
                and ext not in self.ignore_extensions
            ]
        ]

    class Const:
        test_guild = 738060171519197294

    
    
    async def setup_hook(self):
        await self.load_extension("utils.logger")
        self.logger: logging.Logger = self.get_cog("Logger")
        self.logger.setLevel("info")
        self.session = aiohttp.ClientSession()
        for ext in self.extensions_path:
            try:
                await self.load_extension(ext)
            except (
                commands.ExtensionNotFound,
                commands.ExtensionError,
                commands.ExtensionFailed,
            ) as e:
                self.logger.error(f"Failed to load extension '{ext}'. Skipping... {e}")

        self.logger.info("Extensions loaded")
        self.tree.copy_global_to(guild=discord.Object(self.Const.test_guild))
        
        self.logger.debug("")
        self.logger.debug("===== (REBOOT) =====")
        self.logger.debug("")
        self.logger.success("Client class has been initialized")

    async def close(self):
        await self.session.close()
        await super().close()
    

    async def on_ready(self):
        self.logger.success(f"Logged on as {self.user}")

    async def on_command_error(self, ctx:commands.Context, error):
        ignored = (commands.CommandNotFound,)
        read_args = (commands.NotOwner,)
        if isinstance(error, read_args):
            e = Embed(title="Error", description=f"Error: `{error.args[0]}`")
            await ctx.send(embed=e)
            return
        elif isinstance(error, ignored):
            return
            
        else:
            e = Embed(
                title="Error", description=f"There has been an error:"
            )
            traceback = "".join(
                tb.format_exception(type(error), error, error.__traceback__)
            )
            self.logger.error(traceback)
            link = await self.post_code(traceback)
            if len(traceback) >= 2000:
                traceback = f"Error too long use the link provided below."
            e.description += f"\n```py\n{traceback}```\nError also located here: {link}"

            await ctx.send(embed=e)

            


    async def post_code(self, code:str) -> str:
        posted = await self.session.post("https://hastebin.com/documents", data=code)
        key = (await posted.json())["key"]
        link = f"https://hastebin.com/{key}.py"
        self.logger.debug(f"New hastebin link created: {link}")
        return link