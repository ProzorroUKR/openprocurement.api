from decimal import Decimal
from uuid import uuid4

from schematics.types import BaseType, MD5Type, StringType, URLType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import AmountPercentageValue
from openprocurement.api.procedure.types import DecimalType, IsoDateTimeType
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod
from openprocurement.tender.core.procedure.models.value import (
    ARMAMinExpectedIncome,
    BasicValue,
    EstimatedValue,
    PostEstimatedValue,
    Value,
)
from openprocurement.tender.esco.procedure.constants import (
    LotMinimalStepPercentageValues,
    LotYearlyPaymentsPercentageRangeValues,
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
    guarantee = ModelType(BasicValue)
    status = StringType(choices=["active"])


class PostLot(PostBaseLot):
    value = ModelType(PostEstimatedValue, required=True)
    minimalStep = ModelType(PostEstimatedValue)
    guarantee = ModelType(BasicValue)


# --- For work from tender ---


class PatchTenderLot(BaseLot, TenderLotMixin):
    value = ModelType(EstimatedValue, required=True)
    minimalStep = ModelType(EstimatedValue)
    guarantee = ModelType(BasicValue)


class PostTenderLot(PostLot, TenderLotMixin):
    pass


class Lot(BaseLot, TenderLotMixin):
    value = ModelType(EstimatedValue, required=True)
    minimalStep = ModelType(EstimatedValue)
    guarantee = ModelType(BasicValue)

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()
    numberOfBids = BaseType()  # deprecated


# --- ESCO ---


class ESCOPostLot(PostBaseLot):
    minimalStepPercentage = DecimalType(
        min_value=LotMinimalStepPercentageValues.MIN_VALUE,
        max_value=LotMinimalStepPercentageValues.MAX_VALUE,
        precision=LotMinimalStepPercentageValues.PRECISION,
    )
    guarantee = ModelType(BasicValue)
    yearlyPaymentsPercentageRange = DecimalType(
        default=Decimal("0.8"),
        min_value=LotYearlyPaymentsPercentageRangeValues.MIN_VALUE,
        max_value=LotYearlyPaymentsPercentageRangeValues.MAX_VALUE,
        precision=LotYearlyPaymentsPercentageRangeValues.PRECISION,
    )


class ESCOPatchLot(BaseLot):
    title = StringType()
    guarantee = ModelType(BasicValue)
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


class ESCOPostTenderLot(ESCOPostLot, TenderLotMixin):
    minValue = ModelType(  # TODO: probably this shouldn't be in this procedure type
        PostEstimatedValue,
        required=False,
        default={"currency": "UAH", "valueAddedTaxIncluded": False},
    )
    fundingKind = StringType(choices=["budget", "other"], required=True, default="other")


class ESCOPatchTenderLot(BaseLot, TenderLotMixin):
    minValue = ModelType(PostEstimatedValue)
    guarantee = ModelType(BasicValue)
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


class ESCOLot(BaseLot, TenderLotMixin):
    minValue = ModelType(PostEstimatedValue)
    minimalStepPercentage = DecimalType(
        min_value=LotMinimalStepPercentageValues.MIN_VALUE,
        max_value=LotMinimalStepPercentageValues.MAX_VALUE,
        precision=LotMinimalStepPercentageValues.PRECISION,
    )
    guarantee = ModelType(BasicValue)
    fundingKind = StringType(choices=["budget", "other"], required=True)
    yearlyPaymentsPercentageRange = DecimalType(
        min_value=LotYearlyPaymentsPercentageRangeValues.MIN_VALUE,
        max_value=LotYearlyPaymentsPercentageRangeValues.MAX_VALUE,
        precision=LotYearlyPaymentsPercentageRangeValues.PRECISION,
    )

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()


# --- ARMA ---


class ARMAPostLot(PostBaseLot):
    value = ModelType(AmountPercentageValue, required=True)
    minimalStep = ModelType(AmountPercentageValue)
    guarantee = ModelType(BasicValue)
    minExpectedIncome = ModelType(ARMAMinExpectedIncome)


class ARMAPatchLot(BaseLot):
    title = StringType()
    value = ModelType(AmountPercentageValue)
    minimalStep = ModelType(AmountPercentageValue)
    guarantee = ModelType(BasicValue)
    minExpectedIncome = ModelType(ARMAMinExpectedIncome)
    status = StringType(choices=["active"])


class ARMAPostTenderLot(ARMAPostLot, TenderLotMixin):
    pass


class ARMAPatchTenderLot(BaseLot, TenderLotMixin):
    value = ModelType(AmountPercentageValue)
    minimalStep = ModelType(AmountPercentageValue)
    guarantee = ModelType(BasicValue)
    minExpectedIncome = ModelType(ARMAMinExpectedIncome)


class ARMALot(BaseLot, TenderLotMixin):
    value = ModelType(AmountPercentageValue, required=True)
    minimalStep = ModelType(AmountPercentageValue)
    guarantee = ModelType(BasicValue)
    minExpectedIncome = ModelType(ARMAMinExpectedIncome)

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()


# --- CFA selection: lots come from the agreement, value/minimalStep are calculated ---


class CFASelectionPostLot(PostBaseLot):
    guarantee = ModelType(BasicValue)


class CFASelectionPatchLot(BaseLot):
    title = StringType()
    guarantee = ModelType(BasicValue)
    minimalStep = ModelType(Value)
    status = StringType(choices=["active"])


class CFASelectionPostTenderLot(CFASelectionPostLot, TenderLotMixin):
    pass


class CFASelectionPatchTenderLot(BaseLot, TenderLotMixin):
    title = StringType()
    guarantee = ModelType(BasicValue)
    minimalStep = ModelType(Value)


class CFASelectionLot(BaseLot, TenderLotMixin):
    id = MD5Type(required=True)
    value = ModelType(EstimatedValue)
    minimalStep = ModelType(Value)
    guarantee = ModelType(BasicValue)

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()
    numberOfBids = BaseType()  # deprecated


# --- limited (negotiation): no minimalStep / guarantee ---


class LimitedPostLot(PostBaseLot):
    value = ModelType(PostEstimatedValue, required=True)


class LimitedPatchLot(PatchLot):
    title = StringType()
    value = ModelType(EstimatedValue)


class LimitedPostTenderLot(LimitedPostLot, TenderLotMixin):
    pass


class LimitedPatchTenderLot(PatchTenderLot, TenderLotMixin):
    value = ModelType(EstimatedValue, required=True)


class LimitedLot(BaseLot, TenderLotMixin):
    value = ModelType(EstimatedValue, required=True)
