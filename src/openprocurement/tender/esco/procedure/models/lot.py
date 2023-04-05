from enum import Enum

from schematics.types.compound import ModelType
from schematics.types import URLType, StringType
from schematics.types.serializable import serializable
from decimal import Decimal

from openprocurement.api.models import DecimalType, MD5Type
from openprocurement.tender.core.procedure.models.guarantee import (
    Guarantee,
    PostGuarantee,
    Value,
    PostValue,
)
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod
from openprocurement.tender.core.procedure.models.lot import (
    PostBaseLot,
    PatchBaseLot as BasePatchBaseLot,
    BaseLot,
    TenderLotMixin,
    LotGuaranteeSerializerMixin,
)
from openprocurement.tender.esco.procedure.constants import (
    LotMinimalStepPercentageValues,
    LotYearlyPaymentsPercentageRangeValues,
)


class LotSerializersMixin(LotGuaranteeSerializerMixin):

    @serializable(serialized_name="fundingKind")
    def lot_fundingKind(self):
        return self.get_tender().get("fundingKind", "other")

    @serializable(serialized_name="minValue", type=ModelType(Value))
    def lot_minValue(self):
        tender = self.get_tender()
        return Value(
            dict(
                amount=0,
                currency=tender["minValue"]["currency"],
                valueAddedTaxIncluded=tender["minValue"]["valueAddedTaxIncluded"],
            )
        )


class PatchBaseLot(BasePatchBaseLot):
    minimalStepPercentage = DecimalType(
        min_value=LotMinimalStepPercentageValues.MIN_VALUE,
        max_value=LotMinimalStepPercentageValues.MAX_VALUE,
        precision=LotMinimalStepPercentageValues.PRECISION,
    )
    yearlyPaymentsPercentageRange = DecimalType(
        min_value=LotYearlyPaymentsPercentageRangeValues.MIN_VALUE,
        max_value=LotYearlyPaymentsPercentageRangeValues.MAX_VALUE,
        precision=LotYearlyPaymentsPercentageRangeValues.PRECISION,
    )


class PostLot(PostBaseLot, LotSerializersMixin):
    minimalStepPercentage = DecimalType(
        min_value=LotMinimalStepPercentageValues.MIN_VALUE,
        max_value=LotMinimalStepPercentageValues.MAX_VALUE,
        precision=LotMinimalStepPercentageValues.PRECISION,
    )
    guarantee = ModelType(PostGuarantee)
    yearlyPaymentsPercentageRange = DecimalType(
        default=Decimal("0.8"),
        min_value=LotYearlyPaymentsPercentageRangeValues.MIN_VALUE,
        max_value=LotYearlyPaymentsPercentageRangeValues.MAX_VALUE,
        precision=LotYearlyPaymentsPercentageRangeValues.PRECISION,
    )


class PatchLot(PatchBaseLot):
    title = StringType()
    guarantee = ModelType(Guarantee)


class PostTenderLot(PostLot, TenderLotMixin):
    minValue = ModelType(  # TODO: probably this shouldn't be in this procedure type
        PostValue,
        required=False,
        default={"amount": 0, "currency": "UAH", "valueAddedTaxIncluded": True},
    )
    fundingKind = StringType(choices=["budget", "other"], required=True, default="other")


class PatchTenderLot(PatchBaseLot, TenderLotMixin):
    minValue = ModelType(Value)
    guarantee = ModelType(Guarantee)
    fundingKind = StringType(choices=["budget", "other"])


class Lot(BaseLot, TenderLotMixin, LotSerializersMixin):
    minValue = ModelType(Value)
    minimalStepPercentage = DecimalType(
        min_value=LotMinimalStepPercentageValues.MIN_VALUE,
        max_value=LotMinimalStepPercentageValues.MAX_VALUE,
        precision=LotMinimalStepPercentageValues.PRECISION,
    )
    guarantee = ModelType(Guarantee)
    fundingKind = StringType(choices=["budget", "other"], required=True)
    yearlyPaymentsPercentageRange = DecimalType(
        min_value=LotYearlyPaymentsPercentageRangeValues.MIN_VALUE,
        max_value=LotYearlyPaymentsPercentageRangeValues.MAX_VALUE,
        precision=LotYearlyPaymentsPercentageRangeValues.PRECISION,
    )

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()

