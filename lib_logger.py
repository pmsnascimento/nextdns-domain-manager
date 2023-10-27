'''
lib_logger
'''
import logging
import time



class MilliSecondFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
            s += f".{record.msecs:03.0f}"
        else:
            t = time.strftime(self.default_time_format, ct)
            s = self.default_msec_format % (t, record.msecs)
        return s

class ColoredFormatter(MilliSecondFormatter):
    COLORS = {
        'ERROR': '\033[91m',  # Red
        'WARNING': '\033[93m',  # Yellow
        'INFO': '\033[92m',  # Green
        'DEBUG': '\033[94m',  # Blue
        'RESET': '\033[0m'  # Reset to default color
    }

    def format(self, record):
        log_message = super().format(record)
        log_level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        return f"{log_level_color}{log_message}{self.COLORS['RESET']}"

def setup_logger():
    current_time = time.strftime("%Y%m%d-%H%M%S")
    log_filename = f"nextdns-blocklist-updater_{current_time}.log"

    formatter = ColoredFormatter(fmt="%(asctime)s - [%(levelname)s]  : :  %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # File handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Get the root logger and set its level to DEBUG
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_info(message):
    logging.info(message)


def log_error(message):
    logging.error(message)


def log_warning(message):
    logging.warning(message)


def log_debug(message):
    logging.debug(message)
