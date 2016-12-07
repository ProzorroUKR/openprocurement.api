# -*- coding: utf-8 -*-
from logging import getLogger
from pkg_resources import get_distribution


PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)


def includeme(config):
    LOGGER.info('Init historical.tender plugin.')
