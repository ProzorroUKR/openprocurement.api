from decimal import Decimal
from typing import Annotated, Literal

from pydantic import Field

from openprocurement.api.procedure.types import (
    DecimalOf,
    Url,
)
from openprocurement.tender.core.procedure.models.lot import BaseLot, PostBaseLot, TenderLotMixin
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod
from openprocurement.tender.core.procedure.models.value import BasicValue, PostEstimatedValue
from openprocurement.tender.esco.procedure.constants import (
    LotMinimalStepPercentageValues,
    LotYearlyPaymentsPercentageRangeValues,
)


class ESCOPostLot(PostBaseLot):
    minimalStepPercentage: Annotated[Decimal, DecimalOf(LotMinimalStepPercentageValues.PRECISION)] | None = Field(
        None, ge=LotMinimalStepPercentageValues.MIN_VALUE, le=LotMinimalStepPercentageValues.MAX_VALUE
    )
    guarantee: BasicValue | None = None
    yearlyPaymentsPercentageRange: Annotated[Decimal, DecimalOf(LotYearlyPaymentsPercentageRangeValues.PRECISION)] = (
        Field(
            Decimal("0.8"),
            ge=LotYearlyPaymentsPercentageRangeValues.MIN_VALUE,
            le=LotYearlyPaymentsPercentageRangeValues.MAX_VALUE,
        )
    )


class ESCOPatchLot(BaseLot):
    title: str | None = None
    guarantee: BasicValue | None = None
    minimalStepPercentage: Annotated[Decimal, DecimalOf(LotMinimalStepPercentageValues.PRECISION)] | None = Field(
        None, ge=LotMinimalStepPercentageValues.MIN_VALUE, le=LotMinimalStepPercentageValues.MAX_VALUE
    )
    yearlyPaymentsPercentageRange: (
        Annotated[Decimal, DecimalOf(LotYearlyPaymentsPercentageRangeValues.PRECISION)] | None
    ) = Field(
        None, ge=LotYearlyPaymentsPercentageRangeValues.MIN_VALUE, le=LotYearlyPaymentsPercentageRangeValues.MAX_VALUE
    )
    status: Literal["active"] | None = None


class ESCOPostTenderLot(ESCOPostLot, TenderLotMixin):
    minValue: PostEstimatedValue = Field({"currency": "UAH", "valueAddedTaxIncluded": False}, validate_default=True)
    fundingKind: Literal["budget", "other"] = "other"


class ESCOPatchTenderLot(BaseLot, TenderLotMixin):
    minValue: PostEstimatedValue | None = None
    guarantee: BasicValue | None = None
    fundingKind: Literal["budget", "other"] | None = None
    minimalStepPercentage: Annotated[Decimal, DecimalOf(LotMinimalStepPercentageValues.PRECISION)] | None = Field(
        None, ge=LotMinimalStepPercentageValues.MIN_VALUE, le=LotMinimalStepPercentageValues.MAX_VALUE
    )
    yearlyPaymentsPercentageRange: (
        Annotated[Decimal, DecimalOf(LotYearlyPaymentsPercentageRangeValues.PRECISION)] | None
    ) = Field(
        None, ge=LotYearlyPaymentsPercentageRangeValues.MIN_VALUE, le=LotYearlyPaymentsPercentageRangeValues.MAX_VALUE
    )


class ESCOLot(BaseLot, TenderLotMixin):
    minValue: PostEstimatedValue | None = None
    minimalStepPercentage: Annotated[Decimal, DecimalOf(LotMinimalStepPercentageValues.PRECISION)] | None = Field(
        None, ge=LotMinimalStepPercentageValues.MIN_VALUE, le=LotMinimalStepPercentageValues.MAX_VALUE
    )
    guarantee: BasicValue | None = None
    fundingKind: Literal["budget", "other"]
    yearlyPaymentsPercentageRange: (
        Annotated[Decimal, DecimalOf(LotYearlyPaymentsPercentageRangeValues.PRECISION)] | None
    ) = Field(
        None, ge=LotYearlyPaymentsPercentageRangeValues.MIN_VALUE, le=LotYearlyPaymentsPercentageRangeValues.MAX_VALUE
    )
    auctionPeriod: LotAuctionPeriod | None = None
    auctionUrl: Url | None = None
