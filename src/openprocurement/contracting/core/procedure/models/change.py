from typing import Any, Literal

from pydantic import Field, field_validator

from openprocurement.api.procedure.models.base import Model, validate_uniq
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)


class BaseChange(Model):
    rationale: str = Field(min_length=1)
    rationale_en: str | None = None
    rationale_ru: str | None = None
    rationaleTypes: list[str] = Field(min_length=1)

    @field_validator("rationaleTypes")
    @classmethod
    def validate_rationale_types_items(cls, value):
        validate_uniq(value)
        return value


class Change(BaseChange):
    id: MD5
    status: Literal["pending", "active"] | None = None
    date: IsoDateTime | None = None
    contractNumber: str | None = None
    dateSigned: IsoDateTime | None = None
    modifications: Any = None
    documents: Any = None
    cancellations: Any = None
    author: str | None = None
