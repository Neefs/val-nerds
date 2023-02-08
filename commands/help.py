import discord
from discord import Embed
from discord.ext import commands
from utils.bot import PlaceHolder


class HelpSelect(discord.ui.Select):
    def __init__(self):
        super().__init__()

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: HelpView = self.view

        self.disabled = True
        await self.view.msg.delete()
        for value in self.values:
            await view.helpcommand.send_cog_help(
                view.helpcommand.context.bot.get_cog(value)
            )


class HelpView(discord.ui.View):
    def __init__(
        self, helpcommand: commands.HelpCommand, select: HelpSelect, msg=None
    ) -> None:
        self.helpcommand = helpcommand
        self.msg = msg
        super().__init__(timeout=60)
        self.add_item(select)

    async def on_timeout(self) -> None:
        try:
            await self.msg.delete()
        except:
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.helpcommand.context.author.id != interaction.user.id:
            await interaction.response.send_message(
                ephemeral=True,
                embed=Embed(
                    title="Only the author can use interactions.", color=0xFF0000
                ),
            )
        return self.helpcommand.context.author.id == interaction.user.id


class HelpCommand(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.command_attrs["help"] = "Shows this amazing hand crafted help command."

    def better_command_signature(self, command):
        return "%s%s %s" % (
            self.context.clean_prefix,
            command.qualified_name,
            command.signature,
        )

    async def send_error_message(self, error):
        await self.get_destination().send(
            embed=Embed(title="Error", color=0xFF0000, description=error)
        )

    def no_permission(self, string: str):
        return Embed(
            title=f"You do not have permission to view the help `{string}`",
            color=0xFF0000,
            description=f"You can not view the help for `{string}` because you don"
            "t have access to run that command",
        )

    async def _can_run(self, command: commands.Command, ctx: commands.Context):
        try:
            return await command.can_run(ctx)
        except Exception as e:
            return False

    async def send_bot_help(self, mapping):
        embed = Embed(
            title="Help",
            color=self.context.bot.color,
            description=self.context.bot.description or "Not documented",
        )
        select = HelpSelect()
        for cog in mapping:
            if not isinstance(cog, commands.Cog):
                continue
            cog: commands.Cog = cog

            name = cog.qualified_name
            cmds = 0
            for cmd in cog.get_commands():
                if (
                    self.context.author.id in self.context.bot.devs or not cmd.hidden
                ) and await self._can_run(cmd, self.context):
                    cmds += 1

            if cmds == 0 or (
                name.lower() in ["jishaku", "development"]
                and self.context.author.id not in self.context.bot.devs
            ):
                continue

            embed.add_field(
                name=f"{name}[`{cmds}`]", value=cog.description or "Not documented"
            )
            select.append_option(discord.SelectOption(label=name, value=name))

        view = HelpView(self, select)
        view.msg = await self.get_destination().send(embed=embed, view=view)

    async def send_cog_help(self, cog: commands.Cog):
        ctx = self.context
        embed = Embed(
            title=cog.qualified_name, color=ctx.bot.color, description=cog.description
        )
        commands = ""
        for cmd in cog.get_commands():
            if (
                ctx.author.id in ctx.bot.devs or not cmd.hidden
            ) and await self._can_run(cmd, ctx):
                commands += "\n" + cmd.qualified_name

        embed.add_field(name="Commands", value=commands)
        embed.set_footer(
            text=f"Type {self.context.bot.prefix}help [command] for more info on a command"
        )

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group: commands.Group):
        ctx = self.context
        embed = Embed(
            title=self.get_command_signature(group),
            color=ctx.bot.color,
            description=group.help or "Not documented",
        )
        if len(group.commands) > 0:
            commands = ""
            for cmd in group.commands:
                if (
                    ctx.author.id in ctx.bot.devs or not cmd.hidden
                ) and await self._can_run(cmd, ctx):
                    commands += "\n" + cmd.name
            embed.add_field(name="Commands", value=commands)

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command: commands.Command):
        ctx = self.context
        if not await self._can_run(command, ctx):
            await self.get_destination().send(
                embed=self.no_permission(command.qualified_name)
            )
            return
        embed = Embed(title=self.better_command_signature(command), color=ctx.bot.color)
        embed.add_field(name="Description", value=command.help or "Not Documented")
        embed.add_field(name="Aliases", value=command.aliases or "None")

        await self.get_destination().send(embed=embed)


class Help(commands.Cog):
    """Just a help command"""

    def __init__(self, bot: PlaceHolder):
        self.bot = bot
        self.original_help_command = bot.help_command
        bot.help_command = HelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self.original_help_command

    @commands.Cog.listener()
    async def on_ready(self):
        print("✅ Help cog is ready.")


async def setup(bot):
    await bot.add_cog(Help(bot))
