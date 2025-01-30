import sys
import logging
from datetime import datetime

from lib.fastapi.utils import get_default_timezone

def get_formatter():
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s"
    )
    return formatter


def get_stream_handler():
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(fmt=get_formatter())
    stream_handler.setLevel(level=logging.INFO)
    return stream_handler


def get_file_handler(filename: str):
    file_handler = logging.FileHandler(filename=filename)
    file_handler.setFormatter(fmt=get_formatter())
    return file_handler


# def get_debug_file_handler():
#     filename = f"logs/{datetime.now(tz=get_default_timezone()).strftime('%d.%B.%Y_%A')}_DEBUG.log"
#     file_handler = get_file_handler(filename=filename)
#     file_handler.setLevel(level=logging.DEBUG)
#     return file_handler


# def get_info_file_handler():
#     filename = f"logs/{datetime.now(tz=get_default_timezone()).strftime('%d.%B.%Y_%A')}_INFO.log"
#     file_handler = get_file_handler(filename=filename)
#     file_handler.setLevel(level=logging.INFO)
#     return file_handler


def get_error_file_handler():
    filename = f"logs/{datetime.now(tz=get_default_timezone()).strftime('%d.%B.%Y_%A')}_ERROR.log"
    file_handler = get_file_handler(filename=filename)
    file_handler.setLevel(level=logging.ERROR)
    return file_handler


def get_logger(name: str):
    logger = logging.getLogger(name=name)
    logger.addHandler(hdlr=get_stream_handler())
    # logger.addHandler(hdlr=get_debug_file_handler())
    # logger.addHandler(hdlr=get_info_file_handler())
    logger.addHandler(hdlr=get_error_file_handler())
    return logger


# def get_debug_logger(name:str):
#     return get_logger(name=name, level=logging.DEBUG)

# def get_info_logger(name:str):
#     return get_logger(name=name, level=logging.INFO)

# def get_error_logger(name:str):
#     return get_logger(name=name, level=logging.ERROR)
