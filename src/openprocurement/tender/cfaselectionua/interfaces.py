from zope.interface import Interface
from openprocurement.tender.core.models import ITender


class ICFASelectionUATender(ITender):
    """ Marker interface for closeFrameworkAgreementSelectionUA tenders """

    pass


class ICFASelectionUAChange(Interface):
    """ marker for changes"""
