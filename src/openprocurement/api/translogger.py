import logging
import six

from paste.translogger import TransLogger

try:
    from logging import _nameToLevel as levels
except ImportError:
    from logging import _levelNames as levels


def make_filter(
    app, global_conf,
    logger_name='wsgi',
    format=None,
    logging_level=logging.INFO,
    setup_console_handler=True,
    set_logger_level=logging.DEBUG):
    from paste.util.converters import asbool
    if isinstance(logging_level, (six.binary_type, six.text_type)):
        logging_level = levels[logging_level]
    if isinstance(set_logger_level, (six.binary_type, six.text_type)):
        set_logger_level = levels[set_logger_level]
    return TransLogger(
        app,
        format=format or None,
        logging_level=logging_level,
        logger_name=logger_name,
        setup_console_handler=asbool(setup_console_handler),
        set_logger_level=set_logger_level)
