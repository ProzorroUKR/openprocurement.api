from openprocurement.tender.core.models import ITender
from zope.interface import Interface


class IPriceQuotationTender(ITender):
    """ PriceQuotation Tender marker interface """


class IRequirement(Interface):
    """ Marker for Requirement"""
