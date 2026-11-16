from openprocurement.api.procedure.models.base import DocumentIdMixin, Model
from openprocurement.api.procedure.types import (
    IsoDateTime,
)


class AuctionPeriod(Model):
    startDate: IsoDateTime | None = None


class LotData(Model):
    auctionPeriod: AuctionPeriod | None = None


class TenderChronographData(DocumentIdMixin):
    auctionPeriod: AuctionPeriod | None = None
    lots: list[LotData] | None = None
