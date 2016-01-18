from zope.interface import implementer
from openprocurement.api.models import ITender
from openprocurement.api.models import Tender as BaseTender
from schematics.types import StringType


@implementer(ITender)
class Tender(BaseTender):
    """ OpenEU tender model """

    procurementMethodType = StringType(default="aboveThresholdEU")
    title_en = StringType(required=True)
