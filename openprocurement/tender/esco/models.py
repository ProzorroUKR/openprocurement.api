from zope.interface import implementer
from schematics.types import StringType

from openprocurement.api.models import ITender

from openprocurement.tender.openua.models import (
    Tender as BaseTenderUA,
)

from openprocurement.tender.openeu.models import (
    Tender as BaseTenderEU,
)

from openprocurement.tender.limited.models import (
    ReportingTender as BaseReportingTender,
)


@implementer(ITender)
class Tender(BaseTenderUA):
    """ ESCO UA Tender model """
    procurementMethodType = StringType(default="esco.UA")

TenderESCOUA = Tender


@implementer(ITender)
class Tender(BaseTenderEU):
    """ ESCO EU Tender model """
    procurementMethodType = StringType(default="esco.EU")


TenderESCOEU = Tender


@implementer(ITender)
class Tender(BaseReportingTender):
    """ ESCO Reporting Tender model """
    procurementMethodType = StringType(default="esco.reporting")


TenderESCOReporting = Tender
