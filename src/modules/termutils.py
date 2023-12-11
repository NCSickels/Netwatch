import os
import re
import sys
import ipaddress
import time
import tabulate

from IPy import IP
from rich.console import Console
from rich import print as rprint
import colorama
from termcolor import colored

from modules.sites import sites
from config import parsersettings as settings
from modules import constants
from dataclasses import dataclass, field
from config.config import read_section


class ColorConfig:
    def __init__(self):
        self.console = Console()

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
        if (not settings.colorSupported):
            print(args, kwargs)
            return

        coloredArgs = []
        for arg in args:
            if arg == None or not isinstance(arg, str):
                coloredArgs.append('')
                continue
            coloredArgs.append(color + arg + "\033[1;m")
        print(*coloredArgs, file=sys.stderr, **kwargs)

    # Print only if raw option hasnt been set
    def hprint(self, *args, **kwargs) -> None:
        settings.printHumanFriendlyText
        if (settings.printHumanFriendlyText):
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
            elif (settings.printHumanFriendlyText):
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
        if settings.colorSupported:
            return "%s%s%s" % (self.color, self.text, colorama.Style.RESET_ALL)
        else:
            return self.text


__all__ = ['c', 'use_prop']

# Initialization:
colorama.just_fix_windows_console()


def c(text: str) -> str:
    result = text

    # Colors:
    theme = get_theme()

    for key, color in theme.colors.items():
        styled_portion = re.findall(f"<{key}>(.*?)</{key}>", text)

        if not styled_portion:
            continue

        for portion in styled_portion:
            result = re.sub(f"<{key}>(.*?)</{key}>",
                            colored(portion, color=color),
                            result, 1)

    # Highlights
    for key, highlight in theme.highlights.items():
        styled_portion = re.findall(f"<{key}>(.*?)</{key}>", text)

        if not styled_portion:
            continue

        for portion in styled_portion:
            result = re.sub(f"<{key}>(.*?)</{key}>",
                            colored(portion, on_color=highlight),
                            result, 1)

    # Attributes:
    for key, attribute in theme.attributes.items():
        styled_portion = re.findall(f"<{key}>(.*?)</{key}>", text)

        if not styled_portion:
            continue

        for portion in styled_portion:
            result = re.sub(f"<{key}>(.*?)</{key}>",
                            colored(portion, attrs=attribute),
                            result, 1)

    # Custom Themes:
    for key, style in theme.content.items():
        styled_portion = re.findall(f"<{key}>(.*?)</{key}>", text)

        if not styled_portion:
            continue

        for portion in styled_portion:
            result = re.sub(f"<{key}>(.*?)</{key}>",
                            colored(portion, color=style.color,
                                    on_color=style.highlight, attrs=style.attributes),
                            result, 1)

    return result


def use_prop(text: str, prop: str) -> str:
    style = get_theme().content.get(prop)

    text = f"<{style.color}>{text}</{style.color}>"

    if style.highlight:
        text = f"<{style.highlight}>{text}</{style.highlight}>"

    if style.attributes:
        for attribute in style.attributes:
            text = f"<{attribute}>{text}</{attribute}>"

    return c(text)


def primary(text: str) -> str:
    return c(f"<primary>{text}</primary>")


def warning(text: str) -> str:
    return c(f"<warning>{text}</warning>")


def error(text: str) -> str:
    return c(f"<error>{text}</error>")


def critical(text: str) -> str:
    return c(f"<critical>{text}</critical>")

# Style:


@dataclass
class Style:
    color: str = ''
    highlight: str = ''
    attributes: list[str] = field(default_factory=list)


@dataclass
class Theme:
    content: dict = field(default_factory=dict)

    colors: dict = field(default_factory=dict)
    highlights: dict = field(default_factory=dict)
    attributes: dict = field(default_factory=dict)

    def __post_init__(self):
        self.colors = {
            'grey': 'grey',
            'red': 'red',
            'green': 'green',
            'yellow': 'yellow',
            'blue': 'blue',
            'magenta': 'magenta',
            'cyan': 'cyan',
            'white': 'white'
        }

        self.highlights = {
            'on_grey': 'on_grey',
            'on_red': 'on_red',
            'on_green': 'on_green',
            'on_yellow': 'on_yellow',
            'on_blue': 'on_blue',
            'on_magenta': 'on_magenta',
            'on_cyan': 'on_cyan',
            'on_white': 'on_white'
        }

        self.attributes = {
            'bold': 'bold',
            'dark': 'dark',
            'underline': 'underline',
            'blink': 'blink',
            'reverse': 'reverse',
            'concealed': 'concealed'
        }


theme = Theme()


def get_theme() -> Theme():
    return theme


def set_theme(theme_name: str):
    global theme
    theme = load_theme(theme_name)


def load_theme(theme_name: str) -> Theme:
    theme_section = read_section(theme_name)
    theme_content = dict(theme_section)

    content = {}
    for key, item in theme_content.items():
        style = Style()

        color = re.sub("[\{\[].*?[\}\]]", "", item).strip()

        highlight = re.findall('{(.*?)}', item)
        if highlight:
            highlight = highlight[0]

        attributes = ''.join(re.findall('\[(.*?)\]', item)).split(' ')
        if all(x.isspace() or not x for x in attributes):
            attributes = None

        style.color = color if color else 'white'
        style.highlight = highlight if highlight else None
        style.attributes = attributes if attributes else None

        content[key] = style

    return Theme(content)
