from openprocurement.api.context import get_now
from openprocurement.api.procedure.models.period import Period, PeriodEndRequired
from openprocurement.api.procedure.types import IsoDateTimeType


class QualificationPeriod(Period):
    reportingDatePublication = IsoDateTimeType()


class PostPeriodStartEndRequired(Period):
    startDate = IsoDateTimeType(required=True, default=get_now)  # The state date for the period.
    endDate = IsoDateTimeType(required=True, default=get_now)  # The end date for the period.


class PeriodStartEndRequired(Period):
    startDate = IsoDateTimeType(required=True)  # The state date for the period.
    endDate = IsoDateTimeType(required=True)  # The end date for the period.


class StartedPeriodEndRequired(PeriodEndRequired):
    startDate = IsoDateTimeType(default=lambda: get_now().isoformat())


class EnquiryPeriod(Period):
    clarificationsUntil = IsoDateTimeType()
    invalidationDate = IsoDateTimeType()


class EnquiryPeriodEndRequired(EnquiryPeriod):
    endDate = IsoDateTimeType(required=True)


class StartedEnquiryPeriodEndRequired(EnquiryPeriodEndRequired):
    startDate = IsoDateTimeType(default=lambda: get_now().isoformat())


class LotAuctionPeriod(Period):
    shouldStartAfter = IsoDateTimeType()


class TenderAuctionPeriod(Period):
    shouldStartAfter = IsoDateTimeType()
