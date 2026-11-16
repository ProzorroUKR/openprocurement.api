from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, computed_field, field_validator

from openprocurement.api.procedure.models.base import validate_uniq
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.api.utils import get_now
from openprocurement.contracting.core.procedure.models.change import BaseChange


class PostChange(BaseChange):
    contractNumber: str | None = None
    dateSigned: IsoDateTime | None = None

    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def status(self) -> Any:
        return "pending"

    @computed_field
    def date(self) -> Any:
        return get_now().isoformat()


class PatchChange(BaseChange):
    status: Literal["pending", "active"] | None = None
    rationale: str | None = Field(None, min_length=1)
    rationaleTypes: list[str] | None = Field(None, min_length=1)
    contractNumber: str | None = None
    dateSigned: IsoDateTime | None = None

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
