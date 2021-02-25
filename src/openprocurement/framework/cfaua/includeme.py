from logging import getLogger

from openprocurement.framework.cfaua.models.agreement import Agreement

LOGGER = getLogger("openprocurement.framework.cfaua")


def includeme(config):
    LOGGER.info("Init framework.cfaua plugin.")
    config.add_agreement_agreementTypes(Agreement)
    config.scan("openprocurement.framework.cfaua.views")
