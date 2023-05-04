from openprocurement.api.context import get_now
from openprocurement.api.models import IsoDateTimeType, ValidationError, Value, Period, ListType
from openprocurement.tender.core.procedure.models.base import ModelType
from openprocurement.tender.core.procedure.models.base import BaseAward
from openprocurement.tender.core.procedure.models.organization import PostBusinessOrganization
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.req_response import (
    PatchObjResponsesMixin,
    ObjResponseMixin,
)
from openprocurement.tender.core.procedure.context import get_tender
from schematics.types import StringType, MD5Type, BooleanType, BaseType
from schematics.types.serializable import serializable
from uuid import uuid4


class PostAward(BaseAward):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def date(self):
        return get_now().isoformat()

    status = StringType(required=True, choices=["pending"], default="pending")
    value = ModelType(Value)
    weightedValue = ModelType(Value)
    suppliers = ListType(ModelType(PostBusinessOrganization, required=True), required=True, min_size=1, max_size=1)
    items = ListType(ModelType(Item))
    bid_id = MD5Type(required=True)
    lotID = MD5Type()
    complaintPeriod = ModelType(Period)

    def validate_lotID(self, data, value):
        tender = get_tender()
        if not value and tender.get("lots"):
            raise ValidationError("This field is required.")
        if value and value not in tuple(lot["id"] for lot in tender.get("lots", "") if lot):
            raise ValidationError("lotID should be one of lots")


class PatchAward(PatchObjResponsesMixin, BaseAward):
    status = StringType(choices=["pending", "unsuccessful", "active", "cancelled"])
    qualified = BooleanType()
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    items = ListType(ModelType(Item))


class Award(ObjResponseMixin, BaseAward):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(required=True, choices=["pending", "unsuccessful", "active", "cancelled"])
    date = IsoDateTimeType(required=True)
    value = ModelType(Value)
    weightedValue = ModelType(Value)
    suppliers = ListType(ModelType(PostBusinessOrganization, required=True), required=True, min_size=1, max_size=1)
    bid_id = MD5Type(required=True)
    lotID = MD5Type()
    complaintPeriod = ModelType(Period)
    complaints = BaseType()
    documents = ListType(ModelType(Document, required=True))
    items = ListType(ModelType(Item))

    qualified = BooleanType()
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    def validate_lotID(self, data, value):
        tender = get_tender()
        if not value and tender.get("lots"):
            raise ValidationError("This field is required.")
        if value and value not in tuple(lot["id"] for lot in tender.get("lots", "") if lot):
            raise ValidationError("lotID should be one of lots")
