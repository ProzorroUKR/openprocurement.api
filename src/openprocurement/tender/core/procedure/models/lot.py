from typing import List
from uuid import uuid4

from schematics.types import BaseType, MD5Type, StringType, URLType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from schematics.validate import ValidationError

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType
from openprocurement.tender.core.procedure.models.guarantee import (
    EstimatedValue,
    Guarantee,
    PostEstimatedValue,
    PostGuarantee,
    Value,
)
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod


class BaseLotSerializersMixin(Model):
    def get_tender(self):
        # Looks like kostil :-)
        # if we are using just get_tender(), that's not will work, cause if we updating tender
        # we will get not updated tender data, so we should it use with __parent__
        return self.__parent__ if hasattr(self, "__parent__") and self.__parent__ else get_tender()


class LotGuaranteeSerializerMixin(BaseLotSerializersMixin):
    @serializable(
        serialized_name="guarantee",
        serialize_when_none=False,
        type=ModelType(Guarantee),
    )
    def lot_guarantee(self) -> Guarantee:
        tender = self.get_tender()
        if self.guarantee:
            currency = tender["guarantee"]["currency"] if tender.get("guarantee") else self.guarantee.currency
            return Guarantee({"amount": self.guarantee.amount, "currency": currency})


class LotSerializersMixin(LotGuaranteeSerializerMixin):
    @serializable(serialized_name="minimalStep", type=ModelType(Value), serialize_when_none=False)
    def lot_minimalStep(self) -> Value:
        tender = self.get_tender()
        tender_minimal_step = tender["minimalStep"] if tender.get("minimalStep") else {}
        if tender_minimal_step and self.minimalStep:
            return Value(
                {
                    "amount": self.minimalStep.amount,
                    "currency": tender_minimal_step.get("currency"),
                    "valueAddedTaxIncluded": tender_minimal_step.get("valueAddedTaxIncluded"),
                }
            )

    @serializable(
        serialized_name="value",
        type=ModelType(EstimatedValue),
        serialize_when_none=False,
    )
    def lot_value(self) -> EstimatedValue:
        tender = self.get_tender()
        tender_value = tender["value"] if tender.get("value") else {}
        return EstimatedValue(
            {
                "amount": self.value.amount,
                "currency": tender_value["currency"],
                "valueAddedTaxIncluded": tender_value["valueAddedTaxIncluded"],
            }
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


class PostLot(PostBaseLot, LotSerializersMixin):
    value = ModelType(PostEstimatedValue, required=True)
    minimalStep = ModelType(PostEstimatedValue)
    guarantee = ModelType(PostGuarantee)


# --- For work from tender ---


class PatchTenderLot(BaseLot, TenderLotMixin):
    value = ModelType(EstimatedValue, required=True)
    minimalStep = ModelType(EstimatedValue)
    guarantee = ModelType(Guarantee)


class PostTenderLot(PostLot, TenderLotMixin):
    pass


class Lot(BaseLot, TenderLotMixin, LotSerializersMixin):
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
