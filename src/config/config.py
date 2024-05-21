import configparser
import os.path
from dataclasses import dataclass
from utils.stringutils import convert_to_bool


class ConfigManager:
    "A class for managing configuration files"
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = configparser.ConfigParser()
            # cls._instance.logger = Logger()
            # cls._instance.logger = get_central_logger()
            cls._instance.configFile = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'netwatch.ini')
            cls._instance.themesFile = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), '..', 'themes', 'themes.ini')
            cls._instance.config.read(
                cls._instance.configFile)
            cls._instance.config.read(
                cls._instance.themesFile)
            cls._instance.installDir = os.path.dirname(
                os.path.abspath(__file__)) + '/'
        return cls._instance

    def getConfigFile(self) -> str:
        return self.configFile

    def get(self, section: any, option: any) -> str:
        return self.config.get(section, option)

    def read(self, section: any) -> dict:
        return dict(self.config[section])

    def set(self, section: any, key: any, value: any) -> None:
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, key, value)
            with open(self.configFile, 'w') as f:
                self.config.write(f)
        except Exception as e:
            # self.logger.error(e)
            print(e)

    def getPath(self, section: any, option: any) -> str:
        return self.installDir + self.config.get(section, option)

    def getbool(self, section: str, option: str) -> bool:
        return self.config.getboolean(section, option)


@dataclass
class ConfigResponse:
    response: str = ''

    def as_bool(self) -> bool:
        return convert_to_bool(self.response)


# Read:
def read_section(section_name: str) -> dict:
    config = configparser.ConfigParser()
    config.read(os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 'netwatch.ini'))

    if not config.sections():
        raise FileNotFoundError(
            'Configuration file not found. Try calling \'config.create_default_config_file()\'')

    try:
        section = config[section_name]
        return dict(section)

    except KeyError:
        raise Exception('Invalid section name.')


def read_entry(section_name: str, entry: str) -> ConfigResponse:
    section = read_section(section_name)

    try:
        value = section[entry]
        return ConfigResponse(response=value)

    except KeyError:
        raise Exception('Invalid section or entry name.')


# Update
def update_entry(section_name: str, entry: str, value: str) -> None:
    config = configparser.ConfigParser()
    config.read('./netwatch.ini')
    config.set(section_name, entry, value)

    with open('./netwatch.ini', mode='w') as configfile:
        config.write(configfile)


# Default:
def create_default_config_file():
    if os.path.isfile('./config.ini'):
        return

    config = configparser.ConfigParser()

    config['General'] = {
        'prefix': '>',
        'enable-warnings': 'true'
    }

    config['DefaultTheme'] = {
        'primary': 'white',
        'warning': 'yellow',
        'error': 'red',
        'critical': 'red [bold]'
    }

    with open('./netwatch.ini', mode='w') as configfile:
        config.write(configfile)
