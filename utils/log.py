import logging

from config import config


def create_logger(name, logfile):
    logger = logging.getLogger(name)
    handler = logging.FileHandler("%s/%s" % (config.LOGS_DIR, logfile))
    formatter = logging.Formatter(config.LOGGER_FORMAT)
    
    logger.propagate = False
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(config.LOGGER_DEFAULT_LVL)

    return logger
