import os
import sys

from rich.console import Console
from rich import print as rprint
import colorama

from modules.sites import sites
from config import settings as settings
from modules import constants
# from banners import *


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ColorConfig(metaclass=Singleton):
    def __init__(self):
        self.color_supported = self.check_color_support()
        # self.color_supported = settings.PARSER_SETTINGS.color_supported

    def check_color_support(self):
        return True if (self.color_support() and settings.PARSER_SETTINGS.color_supported) else False

    # Source: https://github.com/django/django/blob/master/django/core/management/color.py
    def color_support(self):
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
        self.colored_print("\033[1;32m", args, kwargs)

    def eprint(self, *args, **kwargs) -> None:
        self.colored_print("\033[1;31m", args, kwargs)

    # Print text with specified color code
    def colored_print(self, color, args, kwargs) -> None:
        color_config = ColorConfig()
        if not color_config.color_supported:
            print(args, kwargs)
            return
        # if (not settings.PARSER_SETTINGS.color_supported):
        #     print(args, kwargs)
        #     return

        colored_args = []
        for arg in args:
            if arg == None or not isinstance(arg, str):
                colored_args.append('')
                continue
            colored_args.append(color + arg + "\033[1;m")
        print(*colored_args, file=sys.stderr, **kwargs)

    # Print only if raw option hasnt been set
    def hprint(self, *args, **kwargs) -> None:
        settings.PARSER_SETTINGS.print_human_friendly_text
        if (settings.PARSER_SETTINGS.print_human_friendly_text):
            print(*args, **kwargs)

    def get_header(self, text: str) -> None:
        return f"\n{text}\n{'-' * len(text)}\n"

    def header(self, text: str) -> None:
        print(self.get_header(text))

    def __str__(self):
        return ""


class Color:
    "A class for colorizing terminal output"

    HEADER = '\033[95m'
    IMPORTANT = '\33[35m'
    NOTICE = '\033[33m'
    BLUE = '\033[34m'  # [1;34m]
    DARK_BLUE = '\x1b[38;5;20m'
    OKBLUE = '\033[94m'
    GREEN = '\033[32m'  # [1;32m]
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    DARK_RED = '\x1b[38;5;1m'
    DARK_PURPLE = '\x1b[38;5;92m'
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

    def add_main(self, text):
        self.entries.append(TextOutputEntry(
            text, constants.TEXT_NORMAL, colorama.Fore.RESET))

    def add_humn(self, text):
        self.entries.append(TextOutputEntry(
            text, constants.TEXT_FRIENDLY, colorama.Style.DIM))

    def add_error(self, text):
        self.entries.append(TextOutputEntry(
            text, constants.TEXT_ERROR, colorama.Fore.RED))

    def add_good(self, text):
        self.entries.append(TextOutputEntry(
            text, constants.TEXT_SUCCESS, colorama.Fore.GREEN))

    def print_to_console(self):
        for line in self.entries:
            should_print = False
            if (line.output == constants.TEXT_NORMAL or line.output == constants.TEXT_ERROR):
                should_print = True
            elif (settings.PARSER_SETTINGS.print_human_friendly_text):
                should_print = True

            if should_print:
                print(line.get_text())


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

    def get_text(self):
        if settings.PARSER_SETTINGS.color_supported:
            return "%s%s%s" % (self.color, self.text, colorama.Style.RESET_ALL)
        else:
            return self.text
