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
from openprocurement.tender.core.procedure.models.lot import (
    PostBaseLot,
    PatchBaseLot,
    BaseLot,
)


class PostLot(PostBaseLot):
    guarantee = ModelType(Guarantee)

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def lot_guarantee(self):
        if self.guarantee:
            currency = self.__parent__.guarantee.currency if self.__parent__.guarantee else self.guarantee.currency
            return Guarantee(dict(amount=self.guarantee.amount, currency=currency))


class PatchLot(PatchBaseLot):
    guarantee = ModelType(Guarantee)
    minimalStep = ModelType(Value)


class Lot(BaseLot):
    value = ModelType(Value)
    minimalStep = ModelType(Value)
    guarantee = ModelType(Guarantee)

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()
    numberOfBids = BaseType()  # deprecated

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def lot_guarantee(self):
        if self.guarantee:
            tender = get_tender()
            currency = tender["guarantee"]["currency"] if "guarantee" in tender else self.guarantee.currency
            return Guarantee(dict(amount=self.guarantee.amount, currency=currency))

    def validate_minimalStep(self, data, value):
        if value and value.amount and data.get("value"):
            if data.get("value").amount < value.amount:
                raise ValidationError("value should be less than value of lot")
