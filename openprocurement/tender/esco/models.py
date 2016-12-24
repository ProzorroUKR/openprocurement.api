from zope.interface import implementer
from schematics.types import StringType

from openprocurement.api.models import ITender

from openprocurement.tender.openua.models import (
    Tender as BaseTenderUA,
)

from openprocurement.tender.openeu.models import (
    Tender as BaseTenderEU,
)


@implementer(ITender)
class Tender(BaseTenderUA):
    """ """
    procurementMethodType = StringType(default="esco.UA")

TenderESCOUA = Tender


@implementer(ITender)
class Tender(BaseTenderEU):
    """ """
    procurementMethodType = StringType(default="esco.EU")


TenderESCOEU = Tender
