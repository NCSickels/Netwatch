import os
import sys

from rich.console import Console
from rich import print as rprint
import colorama

from modules.sites import sites
from config import settings as settings
from modules import constants


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ColorConfig(metaclass=Singleton):
    def __init__(self):
        self.color_supported = self.checkColorSupport()
        # self.color_supported = settings.PARSER_SETTINGS.colorSupported

    def checkColorSupport(self):
        return True if (self.supportsColor() and settings.PARSER_SETTINGS.colorSupported) else False

    # Source: https://github.com/django/django/blob/master/django/core/management/color.py
    def supportsColor(self):
        """
        Returns True if the running system's terminal supports color, and False otherwise.
        """
        platform = sys.platform
        supported_platform = platform != "Pocket PC" and (
            platform != "win32" or "ANSICON" in os.environ)

        # isatty is not always implemented, #6223.
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        return supported_platform and is_a_tty


class LamePrint:
    def __init__(self):
        pass

    # Color output green (successprint)
    def sprint(self, *args, **kwargs) -> None:
        self.coloredPrint("\033[1;32m", args, kwargs)

    def eprint(self, *args, **kwargs) -> None:
        self.coloredPrint("\033[1;31m", args, kwargs)

    # Print text with specified color code
    def coloredPrint(self, color, args, kwargs) -> None:
        color_config = ColorConfig()
        if not color_config.color_supported:
            print(args, kwargs)
            return
        # if (not settings.PARSER_SETTINGS.colorSupported):
        #     print(args, kwargs)
        #     return

        coloredArgs = []
        for arg in args:
            if arg == None or not isinstance(arg, str):
                coloredArgs.append('')
                continue
            coloredArgs.append(color + arg + "\033[1;m")
        print(*coloredArgs, file=sys.stderr, **kwargs)

    # Print only if raw option hasnt been set
    def hprint(self, *args, **kwargs) -> None:
        settings.PARSER_SETTINGS.printHumanFriendlyText
        if (settings.PARSER_SETTINGS.printHumanFriendlyText):
            print(*args, **kwargs)

    def getHeader(self, text: str) -> None:
        return f"\n{text}\n{'-' * len(text)}\n"

    def header(self, text: str) -> None:
        print(self.getHeader(text))

    def __str__(self):
        return ""


class Color:
    "A class for colorizing terminal output"

    HEADER = '\033[95m'
    IMPORTANT = '\33[35m'
    NOTICE = '\033[33m'
    BLUE = '\033[34m'  # [1;34m]
    OKBLUE = '\033[94m'
    GREEN = '\033[32m'  # [1;32m]
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    UNDERLINE = '\033[4m'
    BOLD = '\033[1m'
    LOGGING = '\33[34m'

    # Accent Colors
    AC1 = '#8696ef'


class BannerPrinter:
    "A class for printing banners"

    def __init__(self, logo):
        self.logo = logo
        self.rich_colors = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'bright_black',
                            'bright_red', 'bright_green', 'bright_yellow', 'bright_blue', 'bright_magenta', 'bright_cyan', 'bright_white']
        self.print()

    def print(self) -> None:
        for line in self.logo.split("\n"):
            for character in line:
                if character in ["█"]:
                    rprint(f"[bright_yellow]{character}", end="", flush=True)
                elif character in ["="]:
                    rprint(f"[bright_yellow]{character}", end="", flush=True)
                else:
                    rprint(f"[bright_red]{character}", end="", flush=True)
            print()


class TextOutput():
    def __init__(self):
        self.entries = []

    def addMain(self, text):
        self.entries.append(TextOutputEntry(
            text, constants.TEXT_NORMAL, colorama.Fore.RESET))

    def addHumn(self, text):
        self.entries.append(TextOutputEntry(
            text, constants.TEXT_FRIENDLY, colorama.Style.DIM))

    def addErrr(self, text):
        self.entries.append(TextOutputEntry(
            text, constants.TEXT_ERROR, colorama.Fore.RED))

    def addGood(self, text):
        self.entries.append(TextOutputEntry(
            text, constants.TEXT_SUCCESS, colorama.Fore.GREEN))

    def printToConsole(self):
        for line in self.entries:
            shouldPrint = False
            if (line.output == constants.TEXT_NORMAL or line.output == constants.TEXT_ERROR):
                shouldPrint = True
            elif (settings.PARSER_SETTINGS.printHumanFriendlyText):
                shouldPrint = True

            if shouldPrint:
                print(line.getText())


class TextOutputEntry():
    # Output specified the type of output for the text
    #   0 - Main output
    #   1 - Unnecessary but friendly output (e.g. headings)
    #   2 - Error output
    #   3 - Success/Good output
    def __init__(self, text, output, color):
        self.text = text
        self.output = output
        self.color = color

    def getText(self):
        if settings.PARSER_SETTINGS.colorSupported:
            return "%s%s%s" % (self.color, self.text, colorama.Style.RESET_ALL)
        else:
            return self.text
