# -*- coding: utf-8 -*-
from zope.component import queryUtility

from openprocurement.agreement.cfaua.interfaces import IChange


def get_change_class(instance, data):
    return queryUtility(IChange, data['rationaleType'])
