from openprocurement.api.models import IsoDateTimeType, ValidationError, Value, Period
from openprocurement.tender.core.procedure.models.base import (
    Model, ModelType, ListType, PostBusinessOrganization,
)
from openprocurement.tender.core.procedure.context import get_tender
from schematics.types import StringType, MD5Type
from uuid import uuid4


class Award(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(required=True, choices=["pending", "unsuccessful", "active", "cancelled"])
    date = IsoDateTimeType(required=True)
    value = ModelType(Value, required=True)
    weightedValue = ModelType(Value)
    suppliers = ListType(ModelType(PostBusinessOrganization, required=True), required=True, min_size=1, max_size=1)
    bid_id = MD5Type(required=True)
    lotID = MD5Type()
    complaintPeriod = ModelType(Period)

    def validate_lotID(self, lotID):
        tender = get_tender()
        if not lotID and tender.get("lots"):
            raise ValidationError("This field is required.")
        if lotID and lotID not in tuple(lot["id"] for lot in tender.get("lots", "") if lot):
            raise ValidationError("lotID should be one of lots")
