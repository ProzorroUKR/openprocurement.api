from enum import Enum
from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, StringType, MD5Type
from schematics.types.compound import ListType, ModelType

from openprocurement.api.models import Model
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.complaint_objection_argument import Argument
from openprocurement.tender.core.procedure.models.complaint_objection_requested_remedy import RequestedRemedy


class ObjectionRelatesTo(Enum):
    tender = "tender"
    lot = "lot"
    award = "award"
    qualification = "qualification"
    cancellation = "cancellation"


class Classification(Model):
    scheme = StringType(required=True)
    id = StringType(required=True)
    description = StringType(required=True)


class Objection(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    title = StringType(required=True)
    description = StringType(required=True)
    relatesTo = StringType(choices=[choice.value for choice in ObjectionRelatesTo], required=True)
    relatedItem = StringType(required=True)
    classification = ModelType(Classification, required=True)
    requestedRemedies = ListType(ModelType(RequestedRemedy), min_size=1, required=True)
    arguments = ListType(ModelType(Argument), min_size=1, required=True)

    def validate_relatedItem(self, data, value):
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
        complaint = data.get("__parent__", {})
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


class AwardComplaintObjection(Objection):
    relatesTo = StringType(choices=[ObjectionRelatesTo.award.value, ], required=True)


class CancellationComplaintObjection(Objection):
    relatesTo = StringType(choices=[ObjectionRelatesTo.cancellation.value, ], required=True)


class QualificationComplaintObjection(Objection):
    relatesTo = StringType(choices=[ObjectionRelatesTo.qualification.value, ], required=True)
