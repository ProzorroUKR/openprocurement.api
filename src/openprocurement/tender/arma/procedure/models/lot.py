from typing import Literal

from openprocurement.api.procedure.models.value import AmountPercentageValue
from openprocurement.api.procedure.types import (
    Url,
)
from openprocurement.tender.arma.procedure.models.value import ARMAMinExpectedIncome
from openprocurement.tender.core.procedure.models.lot import BaseLot, PostBaseLot, TenderLotMixin
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod
from openprocurement.tender.core.procedure.models.value import BasicValue


class ARMAPostLot(PostBaseLot):
    value: AmountPercentageValue
    minimalStep: AmountPercentageValue | None = None
    guarantee: BasicValue | None = None
    minExpectedIncome: ARMAMinExpectedIncome | None = None


class ARMAPatchLot(BaseLot):
    title: str | None = None
    value: AmountPercentageValue | None = None
    minimalStep: AmountPercentageValue | None = None
    guarantee: BasicValue | None = None
    minExpectedIncome: ARMAMinExpectedIncome | None = None
    status: Literal["active"] | None = None


class ARMAPostTenderLot(ARMAPostLot, TenderLotMixin):
    pass


class ARMAPatchTenderLot(BaseLot, TenderLotMixin):
    value: AmountPercentageValue | None = None
    minimalStep: AmountPercentageValue | None = None
    guarantee: BasicValue | None = None
    minExpectedIncome: ARMAMinExpectedIncome | None = None


class ARMALot(BaseLot, TenderLotMixin):
    value: AmountPercentageValue
    minimalStep: AmountPercentageValue | None = None
    guarantee: BasicValue | None = None
    minExpectedIncome: ARMAMinExpectedIncome | None = None
    auctionPeriod: LotAuctionPeriod | None = None
    auctionUrl: Url | None = None
