import logging
import sys


FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')

def console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler

def get_logger(logger_name: str):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler())
    logger.propgate = False
    return logger
