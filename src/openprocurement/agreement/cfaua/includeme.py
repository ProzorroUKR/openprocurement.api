from logging import getLogger
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator

from openprocurement.agreement.cfaua.interfaces import IClosedFrameworkAgreementUA
from openprocurement.agreement.cfaua.models.agreement import Agreement
from openprocurement.agreement.cfaua.adapters.configurator import CFAgreementUAConfigurator


LOGGER = getLogger("openprocurement.agreement.cfaua")


def includeme(config):
    LOGGER.info("Init agreement.cfaua plugin.")

    config.add_agreement_type(Agreement)
    config.registry.registerAdapter(
        CFAgreementUAConfigurator, (IClosedFrameworkAgreementUA, IRequest), IContentConfigurator
    )
    config.scan("openprocurement.agreement.cfaua.views")
