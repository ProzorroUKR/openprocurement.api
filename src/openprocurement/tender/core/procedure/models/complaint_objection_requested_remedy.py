from uuid import uuid4

from pydantic import Field, field_validator

from openprocurement.api.constants import REQUESTED_REMEDIES_TYPES
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    MD5,
)


class RequestedRemedy(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    type: str
    description: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, value):
        if value not in REQUESTED_REMEDIES_TYPES:
            raise ValidationError(f"Value must be one of {REQUESTED_REMEDIES_TYPES}")
        return value
