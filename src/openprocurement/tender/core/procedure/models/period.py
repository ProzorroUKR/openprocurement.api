from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import IsoDateTimeType


class QualificationPeriod(Period):
    reportingDatePublication = IsoDateTimeType()


class EnquiryPeriod(Period):
    clarificationsUntil = IsoDateTimeType()
    invalidationDate = IsoDateTimeType()


class LotAuctionPeriod(Period):
    shouldStartAfter = IsoDateTimeType()


class TenderAuctionPeriod(Period):
    shouldStartAfter = IsoDateTimeType()
