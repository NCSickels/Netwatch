import logging
import logging.config
from config.paths import logger_config_file_path

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            'datefmt': "[%Y-%m-%d %H:%M:%S]",
        },
        'colored': {
            '()': 'logger.color_formatter.ColorFormatter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        },
        'colored_console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'colored',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'root': {
            'level': 'INFO',
            'handlers': ['colored_console'],
        },
    },
}


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)

        return cls._instances[cls]


class Logger(metaclass=Singleton):
    """
    The Logger class provides a singleton logger instance for logging messages.

    Usage:
    - Logger.debug("Debug message")
    - Logger.info("Info message")
    - Logger.warning("Warning message")
    - Logger.error("Error message")
    - Logger.critical("Critical message")
    """

    _logger: logging.Logger = None

    def __init__(self):
        logging.config.dictConfig(LOGGING_CONFIG)
        Logger._logger = logging.getLogger()
        # with open(logger_config_file_path, mode='r', encoding='utf-8') as file:
        #     config = yaml.safe_load(file.read())
        #     logging.config.dictConfig(config)

    @classmethod
    def debug(cls, message: str):
        cls._logger.debug(message)

    @classmethod
    def info(cls, message: str):
        cls._logger.info(message)

    @classmethod
    def warning(cls, message: str):
        cls._logger.warning(message)

    @classmethod
    def error(cls, message: str):
        cls._logger.error(message)

    @classmethod
    def critical(cls, message: str):
        cls._logger.critical(message)
