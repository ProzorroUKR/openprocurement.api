from logging import getLogger

LOGGER = getLogger("openprocurement.tender.competitiveordering")


def includeme(config):
    LOGGER.info("Init tender.competitiveordering plugin.")
    config.scan("openprocurement.tender.competitiveordering.procedure.views")
