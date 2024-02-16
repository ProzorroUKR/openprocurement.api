from logging import getLogger

LOGGER = getLogger("openprocurement.tender.competitivedialogue")


def includeme(config):
    LOGGER.info("Init tender.competitivedialogue plugin.")

    # add two types of Competitive Dialogue
    config.scan("openprocurement.tender.competitivedialogue.procedure.views.stage1")
    config.scan("openprocurement.tender.competitivedialogue.procedure.views.stage2")
