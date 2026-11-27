from enum import StrEnum
from typing import Literal
from uuid import uuid4

from pydantic import Field, field_validator

from openprocurement.api.constants import (
    AMCU,
    AMCU_24,
    ARTICLE_16,
    ARTICLE_17,
    ARTICLE_20,
    ARTICLE_21,
    OTHER_CRITERIA,
    VIOLATION_AMCU,
)
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model, model_field_validator, validate_uniq_id
from openprocurement.api.procedure.types import (
    MD5,
)
from openprocurement.tender.core.procedure.models.complaint_objection_argument import (
    Argument,
)
from openprocurement.tender.core.procedure.models.complaint_objection_requested_remedy import (
    RequestedRemedy,
)


class ObjectionRelatesTo(StrEnum):
    tender = "tender"
    lot = "lot"
    award = "award"
    qualification = "qualification"
    cancellation = "cancellation"


OBJECTION_CRITERIA_CLASSIFICATIONS = {
    "article_16": ARTICLE_16,
    "article_17": ARTICLE_17,
    "article_20": ARTICLE_20,
    "article_21": ARTICLE_21,
    "other": OTHER_CRITERIA,
    "violation_amcu": VIOLATION_AMCU,
    "amcu": AMCU,
    "amcu_24": AMCU_24,
}


class Classification(Model):
    scheme: Literal[
        "article_16", "article_17", "article_20", "article_21", "other", "violation_amcu", "amcu", "amcu_24"
    ]
    id: str
    description: str

    @model_field_validator("id")
    def validate_id(self, code):
        scheme = self.scheme
        if code not in OBJECTION_CRITERIA_CLASSIFICATIONS.get(scheme, []):
            raise ValidationError(f"Value must be one of {scheme} reasons")


class Objection(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    title: str
    description: str | None = None
    relatesTo: ObjectionRelatesTo
    relatedItem: str
    classification: Classification
    requestedRemedies: list[RequestedRemedy] = Field(min_length=1)
    arguments: list[Argument] = Field(min_length=1)
    sequenceNumber: int | None = Field(None, ge=0)

    @field_validator("requestedRemedies")
    @classmethod
    def validate_requested_remedies_items(cls, value):
        validate_uniq_id(value)
        return value

    @field_validator("arguments")
    @classmethod
    def validate_arguments_items(cls, value):
        validate_uniq_id(value)
        return value


class TenderComplaintObjection(Objection):
    relatesTo: Literal[ObjectionRelatesTo.tender, ObjectionRelatesTo.lot]


class AwardComplaintObjection(Objection):
    relatesTo: Literal[ObjectionRelatesTo.award]


class CancellationComplaintObjection(Objection):
    relatesTo: Literal[ObjectionRelatesTo.cancellation]


class QualificationComplaintObjection(Objection):
    relatesTo: Literal[ObjectionRelatesTo.qualification]
