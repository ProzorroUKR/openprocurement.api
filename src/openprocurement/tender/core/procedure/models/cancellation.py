from openprocurement.api.context import get_now
from openprocurement.api.models import IsoDateTimeType, ValidationError, ListType, Model
from openprocurement.tender.core.procedure.models.base import ModelType
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.utils import since_2020_rules
from schematics.types import StringType, MD5Type, BaseType
from schematics.types.serializable import serializable
from uuid import uuid4


class PostCancellation(Model):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def date(self):
        return get_now().isoformat()

    @serializable
    def cancellationOf(self):
        return "lot" if self.relatedLot else "tender"

    status = StringType(choices=["draft", "pending", "active"])

    @serializable(serialized_name="status")
    def default_status(self):
        if since_2020_rules():
            return "draft"
        elif not self.status:
            return "pending"
        return self.status

    reasonType = StringType()

    reason = StringType(required=True)
    reason_en = StringType()
    reason_ru = StringType()

    documents = ListType(ModelType(Document, required=True))
    relatedLot = MD5Type()

    def validate_relatedLot(self, data, related_lot):
        if related_lot:
            if not any(l["id"] == related_lot for l in get_tender().get("lots", "")):
                raise ValidationError("relatedLot should be one of lots")

        elif data.get("cancellationOf") == "lot":
            raise ValidationError("This field is required.")


class PatchCancellation(Model):
    status = StringType(choices=["draft", "pending", "active", "unsuccessful"])
    reasonType = StringType()


class Cancellation(Model):
    id = MD5Type(required=True)
    status = StringType(required=True, choices=["draft", "pending", "active", "unsuccessful"])
    date = IsoDateTimeType(required=True)

    reasonType = StringType()

    reason = StringType(required=True)
    reason_en = StringType()
    reason_ru = StringType()

    cancellationOf = StringType(required=True, choices=["lot", "tender"])
    relatedLot = MD5Type()

    complaints = BaseType()
    complaintPeriod = BaseType()
    documents = BaseType()
