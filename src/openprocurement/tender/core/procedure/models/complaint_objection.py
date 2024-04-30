from enum import Enum
from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, IntType, MD5Type, StringType
from schematics.types.compound import ListType, ModelType

from openprocurement.api.constants import (
    AMCU,
    AMCU_24,
    ARTICLE_16,
    ARTICLE_17,
    OTHER_CRITERIA,
    VIOLATION_AMCU,
)
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.tender.core.procedure.context import get_complaint
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
        required=True, choices=["article_16", "article_17", "other", "violation_amcu", "amcu", "amcu_24"]
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
    requestedRemedies = ListType(ModelType(RequestedRemedy), min_size=1, required=True)
    arguments = ListType(ModelType(Argument), min_size=1, required=True)
    sequenceNumber = IntType(min_value=1)

    def validate_relatedItem(self, data, value):
        complaint = get_complaint() or data.get("__parent__", {})
        if complaint.get("status", "draft") == "draft":
            tender = get_tender()
            relates_to = data["relatesTo"]
            if relates_to == ObjectionRelatesTo.tender.value:
                if value != tender.get("_id"):
                    raise ValidationError("Invalid tender id")
            else:
                obj = self.find_related_item(tender, relates_to, value)
                if relates_to in ("award", "qualification") and obj.get("status") not in ("active", "unsuccessful"):
                    raise ValidationError(f"Relate objection to {relates_to} in {obj.get('status')} is forbidden")
        return value

    @staticmethod
    def find_related_item(parent_obj, obj_name, obj_id):
        for obj in parent_obj.get(f'{obj_name}s', []):
            if obj["id"] == obj_id:
                return obj
        raise ValidationError(f"Invalid {obj_name} id")


class TenderComplaintObjection(Objection):
    relatesTo = StringType(
        choices=[obj.value for obj in (ObjectionRelatesTo.tender, ObjectionRelatesTo.lot)],
        required=True,
    )

    def validate_relatedItem(self, data, value):
        super().validate_relatedItem(self, data, value)
        complaint = get_complaint() or data.get("__parent__", {})
        related_lot = complaint.get("relatedLot")
        if data["relatesTo"] == ObjectionRelatesTo.lot.value:
            if not related_lot or value != related_lot:
                raise ValidationError(
                    "Complaint's objection must relate to the same lot id as mentioned in complaint's relatedLot"
                )
        elif related_lot:
            raise ValidationError(
                f"Complaint's objection must not relate to {data['relatesTo']} if relatedLot mentioned"
            )
        return value


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
