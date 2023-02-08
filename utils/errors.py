from discord.ext.commands import CommandError


class NotDeveloper(CommandError):
    def __init__(self):
        super().__init__("You need to be a developer to run that command.")
