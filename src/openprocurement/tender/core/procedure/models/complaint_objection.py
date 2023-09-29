import re
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


OBJECTION_RELATES_REGEX_MAPPING = {
    ObjectionRelatesTo.tender: r"^\/tenders\/(?P<tender_id>[0-9a-fA-F]{32})$",
    ObjectionRelatesTo.lot: (
        r"^"
        r"\/tenders\/(?P<tender_id>[0-9a-fA-F]{32})"
        r"\/"
        r"lots\/(?P<lot_id>[0-9a-fA-F]{32})"
        r"$"
    ),
    ObjectionRelatesTo.award: (
        r"^"
        r"\/tenders\/(?P<tender_id>[0-9a-fA-F]{32})"
        r"\/"
        r"awards\/(?P<award_id>[0-9a-fA-F]{32})"
        r"$"
    ),
    ObjectionRelatesTo.qualification: (
        r"^"
        r"\/tenders\/(?P<tender_id>[0-9a-fA-F]{32})"
        r"\/"
        r"qualifications\/(?P<qualification_id>[0-9a-fA-F]{32})"
        r"$"
    ),
    ObjectionRelatesTo.cancellation: (
        r"^"
        r"\/tenders\/(?P<tender_id>[0-9a-fA-F]{32})"
        r"\/"
        r"cancellations\/(?P<cancellation_id>[0-9a-fA-F]{32})"
        r"$"
    ),
}


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
        related_regex = OBJECTION_RELATES_REGEX_MAPPING[getattr(ObjectionRelatesTo, relates_to)]
        related_re = re.compile(related_regex, re.IGNORECASE)
        related_match = related_re.search(value)
        if not related_match:
            raise ValidationError("Invalid relatedItem pattern")
        url_parts = value.split("/")
        if url_parts[2] != tender.get("_id"):  # tender id in url
            raise ValidationError("Invalid tender id")
        if relates_to != ObjectionRelatesTo.tender.value:
            obj = self.find_related_item(tender, url_parts[3], url_parts[4])
            if relates_to in ("award", "qualification") and obj.get("status") not in ("active", "unsuccessful"):
                raise ValidationError(f"Relate objection to {relates_to} in {obj.get('status')} is forbidden")
        return related_match.groupdict()

    @staticmethod
    def find_related_item(parent_obj, obj_name, obj_id):
        for obj in parent_obj.get(obj_name, []):
            if obj["id"] == obj_id:
                return obj
        raise ValidationError(f"Invalid {obj_name} path")


class TenderComplaintObjection(Objection):
    relatesTo = StringType(
        choices=[obj.value for obj in (ObjectionRelatesTo.tender, ObjectionRelatesTo.lot)],
        required=True,
    )

    def validate_relatedItem(self, data, value):
        super().validate_relatedItem(self, data, value)
        url_parts = value.split("/")
        complaint = data.get("__parent__", {})
        related_lot = complaint.get("relatedLot")
        if data["relatesTo"] == ObjectionRelatesTo.lot.value:
            if not related_lot or url_parts[-1] != related_lot:
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
