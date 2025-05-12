from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules


class PostCancellation(Model):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def date(self):
        return get_request_now().isoformat()

    @serializable
    def cancellationOf(self):
        return "lot" if self.relatedLot else "tender"

    status = StringType(choices=["draft", "pending", "active"])

    @serializable(serialized_name="status")
    def default_status(self):
        if tender_created_after_2020_rules():
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
            if not any(lot["id"] == related_lot for lot in get_tender().get("lots", "")):
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
