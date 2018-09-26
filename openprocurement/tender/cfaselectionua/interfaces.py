from openprocurement.tender.core.models import ITender
from zope.interface import Interface


class ICFASelectionUATender(ITender):
    """ Marker interface for closeFrameworkAgreementSelectionUA tenders """
    pass


class IValidator(Interface):
    pass


class ISerializable(Interface):
    pass
