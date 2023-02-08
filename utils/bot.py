import os
import traceback as tb

import aiohttp
import discord
import jishaku
import mystbin
from discord import app_commands, Embed
from discord.ext import commands

from utils.errors import NotDeveloper


class PlaceHolder(commands.Bot):
    def __init__(self, **options):
        self.config = options.pop("config")
        self.name = self.config["bot"]["name"]
        self.prefix = self.config["bot"]["prefix"]
        self.devs = self.config["bot"]["developers"]
        self.color = 0xFF0AF0
        super().__init__(commands.when_mentioned_or(self.prefix), **options)

    @property
    def me(self):
        """Alias for bot.user"""
        return self.user

    @property
    def id(self):
        """Alias for bot.user.id"""
        return self.user.id

    async def load_cogs(self, folders: str | list):
        if isinstance(folders, str):
            folders = [folders]
        for folder in folders:
            try:
                for filename in os.listdir(folder):
                    if (
                        self.config["bot"]["helpCommand"] == False
                        and filename[:-3] == "help"
                    ):
                        continue

                    if filename.endswith(".py") and not filename.startswith("_"):
                        await self.load_extension(f"{folder}.{filename[:-3]}")
            except FileNotFoundError:
                print(str(folder) + " Could not be found")

    async def post_code(self, code, lang=None) -> str:
        if not lang:
            lang = "python"
        client = mystbin.Client()
        returned = await self.client.create_paste(filename=f"code.{lang}", content=code, syntax=lang)
        await client.close()
        return returned

    async def starting_logic(self):
        await self.load_cogs(["commands", "events"])
        await self.load_extension("jishaku")
        if self.config["bot"]["helpCommand"] == False:
            self.help_command = None

    async def closing_logic(self):
        await self.close()


class BotCommandTree(app_commands.CommandTree):
    def __init__(self, client):
        super().__init__(client)

    async def on_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:

        read_args = (NotDeveloper,)
        if isinstance(error, read_args):

            await interaction.response.send_message(
                embed=Embed(
                    title="Error",
                    color=0xFF0000,
                    description="Error: `{0}`".format(error.args[0]),
                ),
                ephemeral=True,
            )
        else:
            e = Embed(
                title="Error", color=0xFF0000, description=f"There has been an error:"
            )
            traceback = "".join(
                tb.format_exception(type(error), error, error.__traceback__)
            )
            link = await self.client.post_code(traceback, "bash")
            if len(traceback) >= 2000:
                traceback = f"Error too long use the link provided below."
            e.description += f"\n```py\n{traceback}```\nError also located here: {link}"

            try:
                await interaction.response.send_message(embed=e, ephemeral=True)
            except discord.InteractionResponded:
                await interaction.channel.send(
                    "The interaction was already responded to so I had to send in a message everyone can see.",
                    embed=e,
                )

            print("Ignoring exception in command {}:".format(interaction.command.name))
            tb.print_exception(type(error), error, error.__traceback__)
