from zope.interface import Interface
from openprocurement.agreement.core.interfaces import IAgreement


class IClosedFrameworkAgreementUA(IAgreement):
    """ marker for CFAUA agreements"""


class IChange(Interface):
    """ marker for changes"""
