import logging
from modules.colorhelper import c, use_prop
# from logger import NOTICE
# BUG: Critical logging message showing tags in the console instead of color


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
