from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.types import (
    IsoDateTime,
)


class QualificationPeriod(Period):
    reportingDatePublication: IsoDateTime | None = None


class EnquiryPeriod(Period):
    clarificationsUntil: IsoDateTime | None = None
    invalidationDate: IsoDateTime | None = None


class LotAuctionPeriod(Period):
    shouldStartAfter: IsoDateTime | None = None


class TenderAuctionPeriod(Period):
    shouldStartAfter: IsoDateTime | None = None
