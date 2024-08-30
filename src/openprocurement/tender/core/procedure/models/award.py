from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, BooleanType, MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.tender.core.procedure.models.award_milestone import (
    AwardMilestoneListMixin,
)
from openprocurement.tender.core.procedure.models.base import BaseAward
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.organization import (
    BusinessOrganization,
)
from openprocurement.tender.core.procedure.models.req_response import (
    ObjResponseMixin,
    PatchObjResponsesMixin,
)


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
    suppliers = ListType(ModelType(BusinessOrganization, required=True), required=True, min_size=1, max_size=1)
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
    eligible = BooleanType()
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    items = ListType(ModelType(Item))


class Award(AwardMilestoneListMixin, ObjResponseMixin, BaseAward):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(required=True, choices=["pending", "unsuccessful", "active", "cancelled"])
    date = IsoDateTimeType(required=True)
    value = ModelType(Value)
    weightedValue = ModelType(Value)
    suppliers = ListType(ModelType(BusinessOrganization, required=True), required=True, min_size=1, max_size=1)
    bid_id = MD5Type(required=True)
    lotID = MD5Type()
    complaintPeriod = ModelType(Period)
    complaints = BaseType()
    documents = ListType(ModelType(Document, required=True))
    items = ListType(ModelType(Item))
    period = ModelType(Period)

    qualified = BooleanType(default=False)
    eligible = BooleanType(default=False)
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

    def validate_qualified(self, data, qualified):
        if data["status"] == "active" and not qualified:
            raise ValidationError("Can't update award to active status with not qualified")
        if data["status"] == "unsuccessful" and (qualified and data.get("eligible", True)):
            raise ValidationError(
                "Can't update award to unsuccessful status when qualified or eligible isn't set to False"
            )

    def validate_eligible(self, data, eligible):
        if data["status"] == "active" and not eligible:
            raise ValidationError("Can't update award to active status with not eligible")
