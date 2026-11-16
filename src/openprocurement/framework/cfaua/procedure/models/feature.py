from decimal import Decimal
from typing import Annotated, Literal
from uuid import uuid4

from pydantic import Field, field_validator

from openprocurement.api.procedure.models.base import Model, validate_uniq_value
from openprocurement.api.procedure.types import (
    DecimalOf,
)


class FeatureValue(Model):
    value: Annotated[Decimal, DecimalOf(-3)] = Field(ge=Decimal("0.0"), le=Decimal("0.3"))
    title: str = Field(min_length=1)
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None


class Feature(Model):
    code: str = Field(default_factory=lambda: uuid4().hex, min_length=1)
    featureOf: Literal["tenderer", "lot", "item"] = "tenderer"
    relatedItem: str | None = Field(None, min_length=1)
    title: str = Field(min_length=1)
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    enum: list[FeatureValue] = Field([], min_length=1)

    @field_validator("enum")
    @classmethod
    def validate_enum_items(cls, value):
        validate_uniq_value(value)
        return value
