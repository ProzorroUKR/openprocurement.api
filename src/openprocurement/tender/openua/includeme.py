# -*- coding: utf-8 -*-
from pyramid.interfaces import IRequest
from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.tender.openua.models import Tender, IAboveThresholdUATender
from openprocurement.tender.openua.adapters import TenderAboveThresholdUAConfigurator


def includeme(config):
    config.add_tender_procurementMethodType(Tender)
    config.scan("openprocurement.tender.openua.views")
    config.scan("openprocurement.tender.openua.subscribers")
    config.registry.registerAdapter(
        TenderAboveThresholdUAConfigurator, (IAboveThresholdUATender, IRequest), IContentConfigurator
    )
