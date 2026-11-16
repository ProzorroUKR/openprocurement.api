from decimal import Decimal
from typing import Annotated

from pydantic import Field, field_validator

from openprocurement.api.procedure.models.base import validate_uniq_value
from openprocurement.api.procedure.types import (
    DecimalOf,
)
from openprocurement.tender.core.procedure.models.feature import Feature, FeatureValue


class CFAFeatureValue(FeatureValue):
    value: Annotated[Decimal, DecimalOf(-2)] = Field(ge=Decimal("0.0"), le=Decimal("0.3"))


class CFAFeature(Feature):
    enum: list[CFAFeatureValue] = Field([], min_length=1)

    @field_validator("enum")
    @classmethod
    def validate_enum_items(cls, value):
        validate_uniq_value(value)
        return value
