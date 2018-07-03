# -*- coding: utf-8 -*-
import os
from openprocurement.api.interfaces import IContentConfigurator
from pyramid.interfaces import IRequest
from zope.configuration.xmlconfig import file as ZcmlFile

import openprocurement.frameworkagreement.cfaua
from openprocurement.frameworkagreement.cfaua.adapters.configurator import CloseFrameworkAgreementUAConfigurator
from openprocurement.frameworkagreement.cfaua.interfaces import ICloseFrameworkAgreementUA
from openprocurement.frameworkagreement.cfaua.models.tender import CloseFrameworkAgreementUA

from zope.component import provideAdapter
# from openprocurement.frameworkagreement.cfaua.adapters.serializable.guarantee import SerializableTenderGuarantee
# from openprocurement.frameworkagreement.cfaua.adapters.serializable.minimalstep import SerializableTenderMinimalStep
# from openprocurement.frameworkagreement.cfaua.adapters.serializable.value import TenderMultilotValue
# from openprocurement.frameworkagreement.cfaua.interfaces import ISerializableTenderValue, ISerializableTenderGuarantee, ISerializableTenderMinimalStep

def includeme(config):
    config.add_tender_procurementMethodType(CloseFrameworkAgreementUA)
    config.scan("openprocurement.frameworkagreement.cfaua.views")
    config.scan("openprocurement.frameworkagreement.cfaua.subscribers")
    config.registry.registerAdapter(CloseFrameworkAgreementUAConfigurator,
                                    (ICloseFrameworkAgreementUA, IRequest),
                                    IContentConfigurator)
    ZcmlFile(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configure.zcml'),
        package=openprocurement.frameworkagreement.cfaua
    )
    # provideAdapter(
    #     TenderMultilotValue,
    #     [ICloseFrameworkAgreementUA, ],
    #     ISerializableTenderValue
    # )

    # provideAdapter(
    #     SerializableTenderGuarantee,
    #     [ICloseFrameworkAgreementUA, ],
    #     ISerializableTenderGuarantee
    # )

    # provideAdapter(
    #     SerializableTenderMinimalStep,
    #     [ICloseFrameworkAgreementUA, ],
    #     ISerializableTenderMinimalStep
    # )