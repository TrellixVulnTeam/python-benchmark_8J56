import logging
from benchmark.utils import config_util

CONFIG = config_util.get_config()


def get_logger(name):
    format_string = "%(asctime)s - %(levelname)s - " \
                    "%(module)s:%(lineno)s - %(message)s"
    formatter = logging.Formatter(fmt=format_string)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)

    log_file = CONFIG.get_opt("log_file", "log")
    if log_file is not None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger
