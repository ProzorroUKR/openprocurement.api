from decimal import Decimal

from schematics.types import StringType, URLType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.models.value import EstimatedValue
from openprocurement.api.procedure.types import DecimalType
from openprocurement.tender.core.procedure.models.guarantee import (
    Guarantee,
    PostEstimatedValue,
    PostGuarantee,
)
from openprocurement.tender.core.procedure.models.lot import (
    BaseLot,
    PostBaseLot,
    TenderLotMixin,
)
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod
from openprocurement.tender.esco.procedure.constants import (
    LotMinimalStepPercentageValues,
    LotYearlyPaymentsPercentageRangeValues,
)


class PostLot(PostBaseLot):
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
        PostEstimatedValue,
        required=False,
        default={"currency": "UAH", "valueAddedTaxIncluded": True},
    )
    fundingKind = StringType(choices=["budget", "other"], required=True, default="other")


class PatchTenderLot(BaseLot, TenderLotMixin):
    minValue = ModelType(EstimatedValue)
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


class Lot(BaseLot, TenderLotMixin):
    minValue = ModelType(EstimatedValue)
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
