from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any

from esculator import escp, npv
from pydantic import Field, field_serializer, model_validator

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.errors import FieldError, ValidationError
from openprocurement.api.procedure.models.base import Model, model_field_validator
from openprocurement.api.procedure.models.value import BasicValue
from openprocurement.api.procedure.types import (
    DecimalOf,
    StringDecimal,
    quantize,
)
from openprocurement.tender.core.procedure.utils import dt_from_iso, fraction_to_decimal


class ESCOContractDuration(Model):
    years: int = Field(ge=0, le=15)
    days: int = Field(0, ge=0, le=364)

    @model_field_validator("days")
    def validate_days(self, days):
        if self.years == 15 and days > 0:
            raise ValidationError("max contract duration 15 years")
        if self.years == 0 and days < 1:
            raise ValidationError("min contract duration 1 day")


class ESCOBasicValue(BasicValue):
    amount: Annotated[Decimal, DecimalOf(-2)] | None = Field(None, ge=Decimal("0"))


class ESCOValue(ESCOBasicValue):
    valueAddedTaxIncluded: bool = False
    amountPerformance: Annotated[Decimal, DecimalOf(-2)] | None = None
    yearlyPaymentsPercentage: Annotated[Decimal, DecimalOf(-5)] | None = Field(None, ge=Decimal("0"), le=Decimal("1"))
    annualCostsReduction: list[StringDecimal] | None = None
    contractDuration: ESCOContractDuration | None = None


class ESCOPatchValue(ESCOValue):
    @model_validator(mode="after")
    def validate_annual_costs_reduction(self):
        if self.annualCostsReduction is not None and len(self.annualCostsReduction) != 21:
            raise FieldError("annualCostsReduction", "annual costs reduction should be set for 21 period")
        return self


class ESCODynamicValue(ESCOValue):
    yearlyPaymentsPercentage: Annotated[Decimal, DecimalOf(-5)] = Field(ge=Decimal("0"), le=Decimal("1"))
    annualCostsReduction: list[StringDecimal]
    contractDuration: ESCOContractDuration

    @field_serializer("amountPerformance")
    def serialize_amount_performance(self, value: Any) -> Decimal | None:
        """Calculated energy service contract performance indicator"""
        tender = get_tender()
        return quantize(
            fraction_to_decimal(
                npv(
                    self.contractDuration.years,
                    self.contractDuration.days,
                    self.yearlyPaymentsPercentage,
                    self.annualCostsReduction,
                    dt_from_iso(tender["noticePublicationDate"]),
                    tender["NBUdiscountRate"],
                )
            ),
            -2,
        )

    @field_serializer("amount")
    def serialize_amount(self, value: Any) -> Decimal | None:
        tender = get_tender()
        return quantize(
            fraction_to_decimal(
                escp(
                    self.contractDuration.years,
                    self.contractDuration.days,
                    self.yearlyPaymentsPercentage,
                    self.annualCostsReduction,
                    datetime.fromisoformat(tender["noticePublicationDate"]),
                )
            ),
            -2,
        )

    @model_validator(mode="after")
    def validate_annual_costs_reduction(self):
        if len(self.annualCostsReduction) != 21:
            raise FieldError("annualCostsReduction", "annual costs reduction should be set for 21 period")
        return self


class ESCOWeightedValue(ESCOBasicValue):
    amountPerformance: Annotated[Decimal, DecimalOf(-2)] | None = None
    denominator: Annotated[Decimal, DecimalOf(-3)] | None = None
    addition: Annotated[Decimal, DecimalOf(-2)] | None = None
    valueAddedTaxIncluded: bool | None = None
