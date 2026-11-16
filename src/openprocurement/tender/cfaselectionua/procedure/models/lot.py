from typing import Any, Literal

from openprocurement.api.procedure.types import (
    MD5,
    Url,
)
from openprocurement.tender.core.procedure.models.lot import BaseLot, PostBaseLot, TenderLotMixin
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod
from openprocurement.tender.core.procedure.models.value import BasicValue, EstimatedValue, Value


class CFASelectionPostLot(PostBaseLot):
    guarantee: BasicValue | None = None


class CFASelectionPatchLot(BaseLot):
    title: str | None = None
    guarantee: BasicValue | None = None
    minimalStep: Value | None = None
    status: Literal["active"] | None = None


class CFASelectionPostTenderLot(CFASelectionPostLot, TenderLotMixin):
    pass


class CFASelectionPatchTenderLot(BaseLot, TenderLotMixin):
    title: str | None = None
    guarantee: BasicValue | None = None
    minimalStep: Value | None = None


class CFASelectionLot(BaseLot, TenderLotMixin):
    id: MD5
    value: EstimatedValue | None = None
    minimalStep: Value | None = None
    guarantee: BasicValue | None = None
    auctionPeriod: LotAuctionPeriod | None = None
    auctionUrl: Url | None = None
    numberOfBids: Any = None
