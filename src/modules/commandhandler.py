from .progutils import *
from .updatehandler import *
from .tablecreator import *


class CommandHandler:
    """A class for handling commands from the user"""

    def __init__(self):
        self.commands = {
            "help": self.help,
            "?": self.help,
            "update": self.update,
            "clear": self.clear,
            "cls": self.clear,
            "clean": self.clean,
            "path": self.print_path,
            "pwd": self.print_path,
            "exit": self.exit,
            "quit": self.exit
        }
        self.program = Program()
        self.updateHandler = UpdateHandler()
        self.configManager = ConfigManager()
        self.tableCreator = TableCreator()
        self.logger = Logger()

    def execute(self, command: str, module=None) -> None:
        args = command.split()
        if args[0] in self.commands:
            self.commands[args[0]](*args[1:], module=module)
        else:
            self.logger.warning("Unknown input. Type '?' for help.")

    def help(self, *args, module=None) -> None:
        self.tableCreator.displayTableFromFile(module)

    def update(self, *args, module=None) -> None:
        self.updateHandler.checkForUpdate()

    def clear(self, *args, module=None) -> None:
        self.program.clearScreen()

    def clean(self, *args, module=None) -> None:
        # self.program.clean(self.configManager.getPath(
        #     "general_config", "tooldir"))
        self.program.clean(self.configManager.getPath(
            "general_config", "scandir"))
        self.program.clean(
            self.configManager.getPath("sagemode", "datadir"))
        # self.completed()

    def print_path(self, *args, module=None) -> None:
        self.program.printPath(module)

    def exit(self, *args, module=None) -> None:
        self.program.end()
