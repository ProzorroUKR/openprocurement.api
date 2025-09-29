from typing import List
from uuid import uuid4

from schematics.types import BaseType, MD5Type, StringType, URLType
from schematics.types.compound import ModelType
from schematics.validate import ValidationError

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod
from openprocurement.tender.core.procedure.models.value import (
    EstimatedValue,
    Guarantee,
    PostEstimatedValue,
)


class BaseLot(Model):
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    status = StringType(choices=["active", "cancelled", "unsuccessful", "complete"], default="active")


class TenderLotMixin(Model):
    id = MD5Type(required=True)
    date = IsoDateTimeType()


class PostBaseLot(BaseLot):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(choices=["active"], default="active")


# --- For work from view ---


class PatchLot(BaseLot):
    title = StringType()
    value = ModelType(EstimatedValue)
    minimalStep = ModelType(EstimatedValue)
    guarantee = ModelType(Guarantee)
    status = StringType(choices=["active"])


class PostLot(PostBaseLot):
    value = ModelType(PostEstimatedValue, required=True)
    minimalStep = ModelType(PostEstimatedValue)
    guarantee = ModelType(Guarantee)


# --- For work from tender ---


class PatchTenderLot(BaseLot, TenderLotMixin):
    value = ModelType(EstimatedValue, required=True)
    minimalStep = ModelType(EstimatedValue)
    guarantee = ModelType(Guarantee)


class PostTenderLot(PostLot, TenderLotMixin):
    pass


class Lot(BaseLot, TenderLotMixin):
    value = ModelType(EstimatedValue, required=True)
    minimalStep = ModelType(EstimatedValue)
    guarantee = ModelType(Guarantee)

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()
    numberOfBids = BaseType()  # deprecated


def validate_lots_uniq(lots: List[Lot], *_) -> None:
    if lots:
        ids = [i.id for i in lots]
        if [i for i in set(ids) if ids.count(i) > 1]:
            raise ValidationError("Lot id should be uniq for all lots")
