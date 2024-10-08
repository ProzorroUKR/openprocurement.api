import logging

from paste.translogger import TransLogger
from paste.util.converters import asbool

levels = {
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.FATAL,
    "ERROR": logging.ERROR,
    "WARN": logging.WARNING,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}


def make_filter(
    app,
    global_conf,
    logger_name="wsgi",
    format=None,
    logging_level=logging.INFO,
    setup_console_handler=True,
    set_logger_level=logging.DEBUG,
):
    if isinstance(logging_level, (bytes, str)):
        logging_level = levels[logging_level]
    if isinstance(set_logger_level, (bytes, str)):
        set_logger_level = levels[set_logger_level]
    return TransLogger(
        app,
        format=format or None,
        logging_level=logging_level,
        logger_name=logger_name,
        setup_console_handler=asbool(setup_console_handler),
        set_logger_level=set_logger_level,
    )
