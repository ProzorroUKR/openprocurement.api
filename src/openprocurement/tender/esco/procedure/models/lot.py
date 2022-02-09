from schematics.types.compound import ModelType
from schematics.types import URLType, StringType, MD5Type
from schematics.types.serializable import serializable
from decimal import Decimal
from schematics.validate import ValidationError
from uuid import uuid4
from math import floor, ceil
from openprocurement.api.models import Value, IsoDateTimeType
from openprocurement.tender.core.utils import calc_auction_end_time, normalize_should_start_after
from openprocurement.tender.core.procedure.validation import (
    validate_lotvalue_value,
    validate_relatedlot,
)
from openprocurement.api.models import DecimalType
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
    minValue = ModelType(Value, required=False,  # TODO: probably this shouldn't be in this procedure type
                         default={"amount": 0, "currency": "UAH", "valueAddedTaxIncluded": True})
    minimalStepPercentage = DecimalType(
        required=True,
        min_value=Decimal("0.005"),
        max_value=Decimal("0.03"),
        precision=-5,
    )
    guarantee = ModelType(Guarantee)
    fundingKind = StringType(choices=["budget", "other"], required=True, default="other")
    yearlyPaymentsPercentageRange = DecimalType(
        required=True,
        default=Decimal("0.8"),
        min_value=Decimal("0"),
        max_value=Decimal("1"),
        precision=-5,
    )

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def lot_guarantee(self):
        if self.guarantee:
            currency = self.__parent__.guarantee.currency if self.__parent__.guarantee else self.guarantee.currency
            return Guarantee(dict(amount=self.guarantee.amount, currency=currency))

    @serializable(serialized_name="fundingKind")
    def lot_fundingKind(self):
        return self.__parent__.fundingKind


class PatchLot(PatchBaseLot):
    minValue = ModelType(Value)
    minimalStepPercentage = DecimalType(
        min_value=Decimal("0.005"),
        max_value=Decimal("0.03"),
        precision=-5,
    )
    guarantee = ModelType(Guarantee)
    fundingKind = StringType(choices=["budget", "other"])
    yearlyPaymentsPercentageRange = DecimalType(
        min_value=Decimal("0"), max_value=Decimal("1"), precision=-5
    )


class Lot(BaseLot):
    minValue = ModelType(Value)
    minimalStepPercentage = DecimalType(
        required=True,
        min_value=Decimal("0.005"),
        max_value=Decimal("0.03"),
        precision=-5,
    )
    guarantee = ModelType(Guarantee)
    fundingKind = StringType(choices=["budget", "other"], required=True)
    yearlyPaymentsPercentageRange = DecimalType(
        required=True, min_value=Decimal("0"), max_value=Decimal("1"), precision=-5
    )

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()

    @serializable(serialized_name="guarantee", serialize_when_none=False, type=ModelType(Guarantee))
    def lot_guarantee(self):
        if self.guarantee:
            currency = self.__parent__.guarantee.currency if self.__parent__.guarantee else self.guarantee.currency
            return Guarantee(dict(amount=self.guarantee.amount, currency=currency))

    @serializable(serialized_name="fundingKind")
    def lot_fundingKind(self):
        return self.__parent__.fundingKind
