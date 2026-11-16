from typing import Literal
from uuid import uuid4

from pydantic import Field, field_validator

from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model, validate_uniq_value


class FeatureValue(Model):
    value: float = Field(ge=0.0)
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


def validate_related_items(obj, features):
    if features:
        item_ids = {i.id for i in getattr(obj, "items", None) or []}  # not fields of all the objects
        lot_ids = {i.id for i in getattr(obj, "lots", None) or []}

        for f in features:
            related_item = f.relatedItem
            feature_of = f.featureOf
            if not related_item and feature_of in ("item", "lot"):
                raise ValidationError([{"relatedItem": ["This field is required."]}])

            if feature_of == "item":
                if f.relatedItem not in item_ids:
                    raise ValidationError([{"relatedItem": ["relatedItem should be one of items"]}])

            elif feature_of == "lot" and f.relatedItem not in lot_ids:
                raise ValidationError([{"relatedItem": ["relatedItem should be one of lots"]}])
