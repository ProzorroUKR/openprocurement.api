# -*- coding: utf-8 -*-
from zope.interface import Interface
from openprocurement.tender.core.models import ITender



class ICloseFrameworkAgreementUA(ITender):
     """ Marker interface for CloseFrameworkAgreementUA tenders """
     pass


class ISerializableTenderValue(Interface):
     pass


class ISerializableTenderMinimalStep(Interface):
     pass


class ISerializableTenderGuarantee(Interface):
     pass