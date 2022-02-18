from schematics.types.compound import ModelType
from schematics.types import URLType, StringType, MD5Type, BaseType
from schematics.types.serializable import serializable
from schematics.validate import ValidationError
from uuid import uuid4
from math import floor, ceil
from openprocurement.api.models import Value, IsoDateTimeType
from openprocurement.api.constants import (
    MINIMAL_STEP_VALIDATION_FROM,
    MINIMAL_STEP_VALIDATION_PRESCISSION,
    MINIMAL_STEP_VALIDATION_LOWER_LIMIT,
    MINIMAL_STEP_VALIDATION_UPPER_LIMIT,
)
from openprocurement.tender.core.utils import get_first_revision_date
from openprocurement.tender.core.procedure.context import get_tender, get_now
from openprocurement.tender.core.procedure.models.base import Model
from openprocurement.tender.core.procedure.models.guarantee import Guarantee
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod


def validate_minimal_step(data, value):
    if value and value.amount and data.get("value"):
        if data.get("value").amount < value.amount:
            raise ValidationError("value should be less than value of lot")
    validate_minimal_step_limits(data, value)


class BaseLot(Model):
    id = MD5Type(required=True)
    title = StringType(required=True, min_length=1)
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    date = IsoDateTimeType()
    status = StringType(choices=["active", "cancelled", "unsuccessful", "complete"], default="active")


class PostBaseLot(BaseLot):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(choices=["active"], default="active")


class PatchBaseLot(BaseLot):
    id = MD5Type(required=True)
    status = StringType(choices=["active"])


class PatchLot(PatchBaseLot):
    value = ModelType(Value, required=True)
    minimalStep = ModelType(Value, required=True)
    guarantee = ModelType(Guarantee)

    def validate_minimalStep(self, data, value):
        validate_minimal_step(data, value)


class PostLot(PostBaseLot):
    value = ModelType(Value, required=True)
    minimalStep = ModelType(Value, required=True)
    guarantee = ModelType(Guarantee)

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def lot_guarantee(self):
        if self.guarantee:
            currency = self.__parent__.guarantee.currency if self.__parent__.guarantee else self.guarantee.currency
            return Guarantee(dict(amount=self.guarantee.amount, currency=currency))

    @serializable(serialized_name="minimalStep", type=ModelType(Value))
    def lot_minimalStep(self):
        return Value(
            dict(
                amount=self.minimalStep.amount,
                currency=self.__parent__.minimalStep.currency,
                valueAddedTaxIncluded=self.__parent__.minimalStep.valueAddedTaxIncluded,
            )
        )

    @serializable(serialized_name="value", type=ModelType(Value))
    def lot_value(self):
        return Value(
            dict(
                amount=self.value.amount,
                currency=self.__parent__.value.currency,
                valueAddedTaxIncluded=self.__parent__.value.valueAddedTaxIncluded,
            )
        )

    def validate_minimalStep(self, data, value):
        validate_minimal_step(data, value)


class Lot(BaseLot):
    value = ModelType(Value, required=True)
    minimalStep = ModelType(Value, required=True)
    guarantee = ModelType(Guarantee)

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()
    numberOfBids = BaseType()  # deprecated

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def lot_guarantee(self):
        if self.guarantee:
            currency = self.__parent__.guarantee.currency if self.__parent__.guarantee else self.guarantee.currency
            return Guarantee(dict(amount=self.guarantee.amount, currency=currency))


def validate_lots_uniq(lots, *args):
    if lots:
        ids = [i.id for i in lots]
        if [i for i in set(ids) if ids.count(i) > 1]:
            raise ValidationError("Lot id should be uniq for all lots")


def validate_minimal_step_limits(data, value):
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
