from decimal import Decimal

from schematics.types import StringType, URLType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.types import DecimalType
from openprocurement.tender.core.procedure.models.guarantee import (
    Guarantee,
    PostGuarantee,
    PostValue,
    Value,
)
from openprocurement.tender.core.procedure.models.lot import (
    BaseLot,
    LotGuaranteeSerializerMixin,
    PostBaseLot,
    TenderLotMixin,
)
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod
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
            {
                "amount": 0,
                "currency": tender["minValue"]["currency"],
                "valueAddedTaxIncluded": tender["minValue"]["valueAddedTaxIncluded"],
            }
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


class PatchLot(BaseLot):
    title = StringType()
    guarantee = ModelType(Guarantee)
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
    status = StringType(choices=["active"])


class PostTenderLot(PostLot, TenderLotMixin):
    minValue = ModelType(  # TODO: probably this shouldn't be in this procedure type
        PostValue,
        required=False,
        default={"amount": 0, "currency": "UAH", "valueAddedTaxIncluded": True},
    )
    fundingKind = StringType(choices=["budget", "other"], required=True, default="other")


class PatchTenderLot(BaseLot, TenderLotMixin):
    minValue = ModelType(Value)
    guarantee = ModelType(Guarantee)
    fundingKind = StringType(choices=["budget", "other"])
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
