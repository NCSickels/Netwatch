import readline
from config import ConfigManager
from logger import Logger
from .progutils import Program
from .updatehandler import UpdateHandler
from .tablecreator import TableCreator
from .trie import Trie


class BaseCommandHandler:
    def __init__(self):
        self.commands = {}
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.complete)

    # This method is used for tab completion with the readline library
    def complete(self, text, state) -> str:
        completions = self.command_trie.starts_with(text)
        if state < len(completions):
            return completions[state]
        else:
            return None


class CommandHandler(BaseCommandHandler):
    """A class for handling commands from the user"""

    def __init__(self):
        super().__init__()
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

        self.command_trie = Trie()
        for command in self.commands.keys():
            self.command_trie.insert(command)

    def execute(self, command: str, module=None) -> None:
        args = command.split()
        if args[0] in self.commands:
            self.commands[args[0]](*args[1:], module=module)
        else:
            self.logger.warning("Unknown input. Type '?' for help.")

    def autocomplete(self, command: str) -> str:
        completions = self.command_trie.starts_with(command)
        if len(completions) == 1:
            return completions[0]
        elif len(completions) > 1:
            # If there are multiple completions, you could return the first one,
            # or you could implement some logic to let the user choose from the completions.
            return completions[0]
        else:
            return command

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

    def print_path(self, *args, module=None) -> None:
        self.program.printPath(module)

    def exit(self, *args, module=None) -> None:
        self.program.end()
