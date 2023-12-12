import logging
from modules.colorhelper import c, use_prop


class ColorFormatter(logging.Formatter):
    def format(self, record):
        format_prop = {
            logging.DEBUG: 'primary',
            logging.INFO: 'primary',
            logging.WARNING: 'warning',
            logging.ERROR: 'error',
            logging.CRITICAL: 'critical',
        }
        date_text = c('<green>%(asctime)s</green>')
        message = c('<primary>%(message)s</primary>')
        # Fixed width of 10 for logger_name
        logger_name = c(f'<magenta>{record.name}</magenta>')

        level_prop = format_prop[record.levelno]
        level = use_prop(f'{record.levelname}', level_prop)

        log_format = f"{date_text} | [{level}] {logger_name}: {message}"
        formatter = logging.Formatter(log_format)

        return formatter.format(record)
