from zope.interface import Interface
from openprocurement.api.interfaces import IOPContent


class IAgreement(IOPContent):
    """ Base interface for agreement containder """


class IAgreementBuilder(Interface):
    """ Marker interface for model building utility """