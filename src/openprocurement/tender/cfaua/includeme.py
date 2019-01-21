# -*- coding: utf-8 -*-
import os
from openprocurement.api.interfaces import IContentConfigurator
from pyramid.interfaces import IRequest
from zope.configuration.xmlconfig import file as ZcmlFile
from zope.interface import directlyProvides
import openprocurement.tender.cfaua
from openprocurement.tender.cfaua.adapters.configurator import CloseFrameworkAgreementUAConfigurator
from openprocurement.tender.cfaua.interfaces import ICloseFrameworkAgreementUA
from openprocurement.tender.cfaua.models.tender import CloseFrameworkAgreementUA

from zope.component import provideAdapter
# from openprocurement.tender.cfaua.adapters.serializable.guarantee import SerializableTenderGuarantee
# from openprocurement.tender.cfaua.adapters.serializable.minimalstep import SerializableTenderMinimalStep
# from openprocurement.tender.cfaua.adapters.serializable.value import TenderMultilotValue
# from openprocurement.tender.cfaua.interfaces import ISerializableTenderValue, ISerializableTenderGuarantee, ISerializableTenderMinimalStep

def includeme(config):
    config.add_tender_procurementMethodType(CloseFrameworkAgreementUA)
    config.scan("openprocurement.tender.cfaua.views")
    config.scan("openprocurement.tender.cfaua.subscribers")
    config.registry.registerAdapter(CloseFrameworkAgreementUAConfigurator,
                                    (ICloseFrameworkAgreementUA, IRequest),
                                    IContentConfigurator)
    ZcmlFile(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configure.zcml'),
        package=openprocurement.tender.cfaua
    )
