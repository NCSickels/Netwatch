import colorama
import re
from dataclasses import dataclass, field
from termcolor import colored
from config.config import read_section
from themes.themes import *

__all__ = ['c', 'use_prop']

# Initialization:
colorama.just_fix_windows_console()

# BUG: Formatter does not properly handle attributes from the .ini file


def c(text: str) -> str:
    """
    Applies color styling to the given text based on the current theme.

    Args:
        text (str): The text to be styled.

    Returns:
        str: The styled text.
    """
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
                            colored(portion, attrs=[attribute]),
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
