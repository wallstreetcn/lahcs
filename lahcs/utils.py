import logging

from lahcs import settings


############################################
######   logger setting
############################################

def get_logger(logname, logpath=None):
    logger = logging.getLogger(logname)
    logger.setLevel(settings.LOG_LEVEL)
    formatter = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(settings.LOG_LEVEL)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if logpath:
        fh = logging.FileHandler(logpath)
        fh.setLevel(settings.LOG_LEVEL)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
