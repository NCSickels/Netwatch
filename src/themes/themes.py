import re
from dataclasses import dataclass, field
from config.config import ConfigManager


# Style:
@dataclass
class Style:
    color: str = ''
    highlight: str = ''
    attributes: list[str] = field(default_factory=list)


@dataclass
class Theme:
    """
    Represents a theme configuration with color, highlight, and attribute settings.
    """

    content: dict = field(default_factory=dict)

    colors: dict = field(default_factory=dict)
    highlights: dict = field(default_factory=dict)
    attributes: dict = field(default_factory=dict)

    def __post_init__(self):
        """
        Initializes the default color, highlight, and attribute settings.
        """
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
config = ConfigManager()


def get_theme() -> Theme:
    return theme


def set_theme(theme_name: str):
    global theme
    theme = load_theme(theme_name)


def load_theme(theme_name: str) -> Theme:
    theme_section = config.read(theme_name)
    theme_content = dict(theme_section)
    content = {}
    for key, item in theme_content.items():
        style = Style()

        color = re.sub("[\{\[].*?[\}\]]", "", item).strip()

        highlight = re.findall('{(.*?)}', item)
        if highlight:
            highlight = highlight[0]
        attributes = re.findall('\[(.*?)\]', item)
        if attributes:
            attributes = attributes[0].split(',')
        else:
            attributes = None

        style.color = color if color else 'white'
        style.highlight = highlight if highlight else None
        style.attributes = attributes if attributes else None
        content[key] = style
    return Theme(content)
