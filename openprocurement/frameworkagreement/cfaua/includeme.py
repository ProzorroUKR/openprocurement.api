# -*- coding: utf-8 -*-
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.frameworkagreement.cfaua.interfaces import ICloseFrameworkAgreementUA
from openprocurement.frameworkagreement.cfaua.models.tender import Tender
from openprocurement.frameworkagreement.cfaua.adapters import CloseFrameworkAgreementUAConfigurator


def includeme(config):
    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.frameworkagreement.cfaua.views")
    config.scan("openprocurement.frameworkagreement.cfaua.subscribers")
    config.registry.registerAdapter(CloseFrameworkAgreementUAConfigurator,
                                    (ICloseFrameworkAgreementUA, IRequest),
                                    IContentConfigurator)
