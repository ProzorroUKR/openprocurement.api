from typing import List
from schematics.types.compound import ModelType
from schematics.types import URLType, StringType, MD5Type, BaseType
from schematics.types.serializable import serializable
from schematics.validate import ValidationError
from uuid import uuid4
from math import floor, ceil
from openprocurement.api.context import get_now
from openprocurement.api.models import IsoDateTimeType
from openprocurement.api.constants import (
    MINIMAL_STEP_VALIDATION_FROM,
    MINIMAL_STEP_VALIDATION_PRESCISSION,
    MINIMAL_STEP_VALIDATION_LOWER_LIMIT,
    MINIMAL_STEP_VALIDATION_UPPER_LIMIT,
)
from openprocurement.tender.core.utils import get_first_revision_date
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.base import Model
from openprocurement.tender.core.procedure.models.guarantee import (
    Guarantee,
    Value,
    PostGuarantee,
    PostValue,
)
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod


class BaseLotSerializersMixin(Model):
    def get_tender(self):
        # Looks like kostil :-)
        # if we are using just get_tender(), that's not will work, cause if we updating tender
        # we will get not updated tender data, so we should it use with __parent__
        return (
            self.__parent__
            if hasattr(self, "__parent__") and self.__parent__
            else get_tender()
        )


class LotGuaranteeSerializerMixin(BaseLotSerializersMixin):
    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def lot_guarantee(self) -> Guarantee:
        tender = self.get_tender()
        if self.guarantee:
            currency = tender["guarantee"]["currency"] if tender.get("guarantee") else self.guarantee.currency
            return Guarantee(dict(amount=self.guarantee.amount, currency=currency))


class LotSerializersMixin(LotGuaranteeSerializerMixin):

    @serializable(serialized_name="minimalStep", type=ModelType(Value))
    def lot_minimalStep(self) -> Value:
        tender = self.get_tender()
        tender_minimal_step = tender["minimalStep"] if tender.get("minimalStep") else dict()
        if tender_minimal_step and self.minimalStep:
            return Value(
                dict(
                    amount=self.minimalStep.amount,
                    currency=tender_minimal_step.get("currency"),
                    valueAddedTaxIncluded=tender_minimal_step.get("valueAddedTaxIncluded"),
                )
            )

    @serializable(serialized_name="value", type=ModelType(Value))
    def lot_value(self) -> Value:
        tender = self.get_tender()
        tender_value = tender["value"] if tender.get("value") else dict()
        return Value(
            dict(
                amount=self.value.amount,
                currency=tender_value["currency"],
                valueAddedTaxIncluded=tender_value["valueAddedTaxIncluded"],
            )
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


class PatchBaseLot(BaseLot):
    status = StringType(choices=["active"])

# --- For work from view ---


class PatchLot(PatchBaseLot):
    title = StringType()
    value = ModelType(Value)
    minimalStep = ModelType(Value)
    guarantee = ModelType(Guarantee)


class PostLot(PostBaseLot, LotSerializersMixin):
    value = ModelType(PostValue, required=True)
    minimalStep = ModelType(PostValue)
    guarantee = ModelType(PostGuarantee)

    def validate_minimalStep(self, data: dict, value: Value) -> None:
        validate_minimal_step(data, value)


# --- For work from tender ---


class PatchTenderLot(PatchBaseLot, TenderLotMixin):
    value = ModelType(Value, required=True)
    minimalStep = ModelType(Value)
    guarantee = ModelType(Guarantee)

    def validate_minimalStep(self, data: dict, value: Value) -> None:
        validate_minimal_step(data, value)


class PostTenderLot(PostLot, TenderLotMixin):
    pass


class Lot(BaseLot, TenderLotMixin, LotSerializersMixin):
    value = ModelType(Value, required=True)
    minimalStep = ModelType(Value)
    guarantee = ModelType(Guarantee)

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()
    numberOfBids = BaseType()  # deprecated

    def validate_minimalStep(self, data: dict, value: Value) -> None:
        validate_minimal_step(data, value)


def validate_lots_uniq(lots: List[Lot], *_) -> None:
    if lots:
        ids = [i.id for i in lots]
        if [i for i in set(ids) if ids.count(i) > 1]:
            raise ValidationError("Lot id should be uniq for all lots")


def validate_minimal_step(data: dict, value: Value) -> None:

    if (
        value
        and value.amount
        and data.get("value")
        and data.get("value").amount < value.amount
    ):
        raise ValidationError("value should be less than value of lot")
    validate_minimal_step_limits(data, value)


def validate_minimal_step_limits(data: dict, value: Value) -> None:
    if value and value.amount is not None and data.get("value"):
        tender_created = get_first_revision_date(get_tender(), default=get_now())
        if tender_created > MINIMAL_STEP_VALIDATION_FROM:
            precision_multiplier = 10**MINIMAL_STEP_VALIDATION_PRESCISSION
            lower_step = (floor(float(data.get("value").amount)
                                       * MINIMAL_STEP_VALIDATION_LOWER_LIMIT * precision_multiplier)
                                 / precision_multiplier)
            higher_step = (ceil(float(data.get("value").amount)
                                       * MINIMAL_STEP_VALIDATION_UPPER_LIMIT * precision_multiplier)
                                  / precision_multiplier)
            if higher_step < value.amount or value.amount < lower_step:
                raise ValidationError(
                    "minimalstep must be between 0.5% and 3% of value (with 2 digits precision).")
