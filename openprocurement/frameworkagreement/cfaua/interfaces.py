# -*- coding: utf-8 -*-
from zope.interface import Interface
from openprocurement.tender.core.models import ITender



class ICloseFrameworkAgreementUA(ITender):
     pass


class ISerializableTenderField(Interface):
     pass


class IValidateTenderField(Interface):
     pass