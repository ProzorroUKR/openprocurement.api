from uuid import uuid4

from pydantic import Field, field_validator, model_validator

from openprocurement.api.constants import (
    MILESTONE_ACTIVE_DURATION_TYPES,
    MILESTONE_CODES,
    MILESTONE_DURATION_TYPES,
    MILESTONE_TITLES,
)
from openprocurement.api.constants_env import MILESTONES_VALIDATION_FROM
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.errors import REQUIRED_MESSAGE, FieldErrors, ValidationError
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import MD5
from openprocurement.api.utils import get_first_revision_date
from openprocurement.tender.core.constants import TenderMilestoneType


class Duration(Model):
    days: int = Field(ge=1)
    type: str

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value not in MILESTONE_DURATION_TYPES:  # the archived types are accepted, but not offered
            raise ValueError(f"Value must be one of {list(MILESTONE_ACTIVE_DURATION_TYPES)}.")
        return value


class BaseMilestone(Model):
    """A payment milestone of a tender / contract / agreement"""

    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    title: str
    description: str | None = None
    type: TenderMilestoneType
    code: str
    percentage: float = Field(le=100)
    duration: Duration
    sequenceNumber: int = Field(ge=0)

    @field_validator("percentage")
    @classmethod
    def validate_percentage(cls, value: float) -> float:
        is_positive_float(value)
        return value

    @model_validator(mode="after")
    def validate_type_values(self):
        errors = {}
        if self.title == "anotherEvent" and not self.description:
            errors["description"] = REQUIRED_MESSAGE
        elif self.description and len(self.description) > 2000:
            if get_first_revision_date(get_tender(), default=get_request_now()) > MILESTONES_VALIDATION_FROM:
                errors["description"] = "description should contain at most 2000 characters"
        if self.code not in MILESTONE_CODES[self.type]:
            errors["code"] = f"Value must be one of {MILESTONE_CODES[self.type]}"
        if self.title not in MILESTONE_TITLES[self.type]:
            errors["title"] = f"Value must be one of {MILESTONE_TITLES[self.type]}"
        if errors:
            raise FieldErrors(errors)
        return self


class Milestone(BaseMilestone):
    relatedLot: MD5 | None = None


def is_positive_float(value):
    if value <= 0:
        raise ValidationError("Float value should be greater than 0.")
