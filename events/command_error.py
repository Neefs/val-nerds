import json
import traceback as tb

import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands.errors import (
    BadArgument,
    MissingAnyRole,
    MissingPermissions,
    MissingRequiredArgument,
)
from discord.interactions import InteractionResponse
from utils.errors import NotDeveloper


class CommandError(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        ignored = (commands.CommandNotFound,)
        read_args = (
            commands.BadArgument,
            commands.NoPrivateMessage,
            commands.CheckFailure,
            NotDeveloper,
            commands.DisabledCommand,
        )
        if isinstance(error, ignored):
            return
        elif isinstance(error, read_args):
            await ctx.send(
                embed=Embed(
                    title="Error",
                    color=0xFF0000,
                    description="Error: `{0}`".format(error.args[0]),
                )
            )
            return
        elif hasattr(ctx.command, "on_error"):
            return
        elif isinstance(error, MissingRequiredArgument):

            # aliases = ctx.command.aliases
            # if aliases != []:
            #     alias = "["
            #     for i in aliases:
            #         if (
            #             i == aliases[len(aliases) - 1]
            #         ):  # it is the last item in this list
            #             alias += i + "]"  # just add to string
            #         else:
            #             alias += i + "|"  # add to string with comma and space

            alias = ctx.command.qualified_name

            await ctx.send(
                embed=Embed(
                    title="Error",
                    color=0xFF0000,
                    description=f"Error: `{error.args[0]}`\nCorrect Usage: {ctx.clean_prefix}{alias} {ctx.command.signature}",
                )
            )
            return

        elif isinstance(error, commands.MissingRole):
            await ctx.send(
                embed=Embed(
                    title="Error",
                    color=0xFF0000,
                    description="Error: **Missing role {0}**. \n{0} is required to run this command.".format(
                        error.missing_role.mention
                    ),
                )
            )
            return

        elif isinstance(error, MissingPermissions):
            perms = ""
            for i in error.missing_permissions:
                if i == error.missing_permissions[len(error.missing_permissions) - 1]:
                    perms += i
                elif i == error.missing_permissions[len(error.missing_permissions) - 2]:
                    perms += i + " and/or "
                else:
                    perms += i + ", "
            await ctx.send(
                embed=Embed(
                    title="Error",
                    color=0xFF0000,
                    description="Error: **Missing permission(s)**. \n**{0}** is required to run this command.".format(
                        perms
                    ),
                )
            )
            return

        else:
            e = Embed(
                title="Error", color=0xFF0000, description=f"There has been an error:"
            )
            traceback = "".join(
                tb.format_exception(type(error), error, error.__traceback__)
            )
            link = await self.bot.post_code(traceback, "bash")
            if len(traceback) >= 2000:
                traceback = f"Error too long use the link provided below."
            e.description += f"\n```py\n{traceback}```\nError also located here: {link}"

            await ctx.send(embed=e)

            print("Ignoring exception in command {}:".format(ctx.command))
            tb.print_exception(type(error), error, error.__traceback__)


async def setup(bot):
    await bot.add_cog(CommandError(bot))
