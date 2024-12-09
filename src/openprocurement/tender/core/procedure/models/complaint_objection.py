from enum import Enum
from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import IntType, MD5Type, StringType
from schematics.types.compound import ListType, ModelType

from openprocurement.api.constants import (
    AMCU,
    AMCU_24,
    ARTICLE_16,
    ARTICLE_17,
    OTHER_CRITERIA,
    VIOLATION_AMCU,
)
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.procedure.models.complaint_objection_argument import (
    Argument,
)
from openprocurement.tender.core.procedure.models.complaint_objection_requested_remedy import (
    RequestedRemedy,
)


class ObjectionRelatesTo(Enum):
    tender = "tender"
    lot = "lot"
    award = "award"
    qualification = "qualification"
    cancellation = "cancellation"


OBJECTION_CRITERIA_CLASSIFICATIONS = {
    "article_16": ARTICLE_16,
    "article_17": ARTICLE_17,
    "other": OTHER_CRITERIA,
    "violation_amcu": VIOLATION_AMCU,
    "amcu": AMCU,
    "amcu_24": AMCU_24,
}


class Classification(Model):
    scheme = StringType(
        required=True,
        choices=[
            "article_16",
            "article_17",
            "other",
            "violation_amcu",
            "amcu",
            "amcu_24",
        ],
    )
    id = StringType(required=True)
    description = StringType(required=True)

    def validate_id(self, data, code):
        scheme = data.get("scheme")
        if code not in OBJECTION_CRITERIA_CLASSIFICATIONS.get(scheme, []):
            raise ValidationError(f"Value must be one of {scheme} reasons")


class Objection(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True)
    description = StringType(serialize_when_none=True)
    relatesTo = StringType(choices=[choice.value for choice in ObjectionRelatesTo], required=True)
    relatedItem = StringType(required=True)
    classification = ModelType(Classification, required=True)
    requestedRemedies = ListType(
        ModelType(RequestedRemedy, required=True),
        min_size=1,
        required=True,
        validators=[
            validate_items_uniq,
        ],
    )
    arguments = ListType(
        ModelType(Argument, required=True),
        min_size=1,
        required=True,
        validators=[
            validate_items_uniq,
        ],
    )
    sequenceNumber = IntType(min_value=0, serialize_when_none=True)


class TenderComplaintObjection(Objection):
    relatesTo = StringType(
        choices=[obj.value for obj in (ObjectionRelatesTo.tender, ObjectionRelatesTo.lot)],
        required=True,
    )


class AwardComplaintObjection(Objection):
    relatesTo = StringType(
        choices=[
            ObjectionRelatesTo.award.value,
        ],
        required=True,
    )


class CancellationComplaintObjection(Objection):
    relatesTo = StringType(
        choices=[
            ObjectionRelatesTo.cancellation.value,
        ],
        required=True,
    )


class QualificationComplaintObjection(Objection):
    relatesTo = StringType(
        choices=[
            ObjectionRelatesTo.qualification.value,
        ],
        required=True,
    )
