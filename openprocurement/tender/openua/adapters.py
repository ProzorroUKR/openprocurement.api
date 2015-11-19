# -*- coding: utf-8 -*-
from openprocurement.tender.openua.models import TenderUA
from openprocurement.tender.openua.interfaces import ITenderUA
from openprocurement.api.adapters import makeBaseTender
from pyramid.events import subscriber
from pyramid.events import ApplicationCreated


class makeTenderUA(makeBaseTender):
    model = TenderUA


@subscriber(ApplicationCreated)
def register_adapters(event):
    registry = event.app.registry
    registry.registerAdapter(makeTenderUA, (dict, ), ITenderUA,
                             name='TenderUA')
