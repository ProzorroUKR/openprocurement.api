from uuid import uuid4

from pydantic import Field, field_validator

from openprocurement.api.procedure.models.base import Model, validate_uniq_id
from openprocurement.api.procedure.types import (
    MD5,
)


class Evidence(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    title: str
    description: str | None = None
    relatedDocument: str


class Argument(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    description: str
    evidences: list[Evidence] = []

    @field_validator("evidences")
    @classmethod
    def validate_evidences_items(cls, value):
        validate_uniq_id(value)
        return value
