from typing import Any, Literal
from uuid import uuid4

from pydantic import Field

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
    Url,
)
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod
from openprocurement.tender.core.procedure.models.value import (
    BasicValue,
    EstimatedValue,
    PostEstimatedValue,
)


class BaseLot(Model):
    title: str = Field(min_length=1)
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    status: Literal["active", "cancelled", "unsuccessful", "complete"] = "active"


class TenderLotMixin(Model):
    id: MD5
    date: IsoDateTime | None = None


class PostBaseLot(BaseLot):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    status: Literal["active"] = "active"


class PatchLot(BaseLot):
    title: str | None = None
    value: EstimatedValue | None = None
    minimalStep: EstimatedValue | None = None
    guarantee: BasicValue | None = None
    status: Literal["active"] | None = None


class PostLot(PostBaseLot):
    value: PostEstimatedValue
    minimalStep: PostEstimatedValue | None = None
    guarantee: BasicValue | None = None


class PatchTenderLot(BaseLot, TenderLotMixin):
    value: EstimatedValue
    minimalStep: EstimatedValue | None = None
    guarantee: BasicValue | None = None


class PostTenderLot(PostLot, TenderLotMixin):
    pass


class Lot(BaseLot, TenderLotMixin):
    value: EstimatedValue
    minimalStep: EstimatedValue | None = None
    guarantee: BasicValue | None = None
    auctionPeriod: LotAuctionPeriod | None = None
    auctionUrl: Url | None = None
    numberOfBids: Any = None
