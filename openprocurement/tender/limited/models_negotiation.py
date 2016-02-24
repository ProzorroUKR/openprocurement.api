from zope.interface import implementer
from schematics.types import StringType
from openprocurement.api.models import ITender
from openprocurement.tender.limited.models import Tender as BaseTender


@implementer(ITender)
class Tender(BaseTender):
    """ Negotiation """
    procurementMethodType = StringType(default="negotiation")
