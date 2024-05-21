import logging
import logging.config
from modules.colorhelper import c, use_prop

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            'datefmt': "[%H:%M:%S]",  # Previous: [%Y-%m-%d %H:%M:%S]
        },
        'colored': {
            '()': 'logger.ColorFormatter',
            'format': "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            'datefmt': '[%H:%M:%S]',
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


class ColorFormatter(logging.Formatter):
    """A custom logging formatter that adds color to log messages."""

    # NOTICE = 25
    # logging.addLevelName(NOTICE, "NOTICE")

    def format(self, record):
        format_prop = {
            logging.DEBUG: 'primary',
            logging.INFO: 'primary',
            logging.WARNING: 'warning',
            logging.ERROR: 'error',
            logging.CRITICAL: 'critical',
            # self.NOTICE: 'notice',
        }
        date_text = c('<cyan>%(asctime)s</cyan>')
        message = c('<primary>%(message)s</primary>')
        # Fixed width of 10 for logger_name
        logger_name = c(f'<magenta>{record.name}</magenta>')

        level_prop = format_prop[record.levelno]
        level = use_prop(f'{record.levelname}', level_prop)

        log_format = f"{date_text} | [{level}] {logger_name}: {message}"
        formatter = logging.Formatter(log_format, datefmt='[%H:%M:%S]')

        return formatter.format(record)


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

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Returns the logger instance.
        """
        return cls._logger

    # @classmethod
    # def notice(cls, message: str):
    #     cls._logger.log(NOTICE, message)

    @classmethod
    def debug(cls, message: str):  # Severity: 10
        cls._logger.debug(message)

    @classmethod
    def info(cls, message: str):  # Severity: 20
        cls._logger.info(message)

    @classmethod
    def warning(cls, message: str):  # Severity: 30
        cls._logger.warning(message)

    @classmethod
    def error(cls, message: str):  # Severity: 40
        cls._logger.error(message)

    @classmethod
    def critical(cls, message: str):  # Severity: 50
        cls._logger.critical(message)


def get_central_logger():
    return Logger.get_logger()
