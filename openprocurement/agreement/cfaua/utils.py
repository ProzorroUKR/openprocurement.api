# -*- coding: utf-8 -*-
from zope.component import queryAdapter

from openprocurement.api.interfaces import IContentConfigurator
from openprocurement.agreement.cfaua.interfaces import IChange


def get_tender_class(instance, data):
    return queryAdapter(IChange, IContentConfigurator, data['rationaleType'])
