from openprocurement.api.context import get_now
from openprocurement.api.models import IsoDateTimeType, ValidationError, Value, Period
from openprocurement.tender.core.procedure.models.base import (
    Model,
    ModelType,
    ListType,
)
from openprocurement.tender.core.procedure.models.organization import (
    BusinessOrganization,
    ContactLessBusinessOrganization,
)
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.context import get_tender
from schematics.types import StringType, MD5Type, BooleanType, BaseType
from schematics.types.serializable import serializable
from uuid import uuid4


class AwardValue(Value):
    valueAddedTaxIncluded = BooleanType(required=True, default=lambda: get_tender()["value"]["valueAddedTaxIncluded"])
    currency = StringType(required=True, max_length=3, min_length=3, default=lambda: get_tender()["value"]["currency"])


class PostBaseAward(Model):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def date(self):
        return get_now().isoformat()

    qualified = BooleanType()
    status = StringType(required=True, choices=["pending"], default="pending")
    value = ModelType(AwardValue, required=True)
    weightedValue = ModelType(AwardValue)
    suppliers = ListType(ModelType(BusinessOrganization, required=True), required=True, min_size=1, max_size=1)
    subcontractingDetails = StringType()


class PatchBaseAward(Model):
    qualified = BooleanType()
    status = StringType(choices=["pending", "unsuccessful", "active", "cancelled"])
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    suppliers = ListType(ModelType(BusinessOrganization, required=True), min_size=1, max_size=1)
    subcontractingDetails = StringType()
    value = ModelType(AwardValue)


class BaseAward(Model):
    id = MD5Type(required=True)
    qualified = BooleanType()
    status = StringType(required=True, choices=["pending", "unsuccessful", "active", "cancelled"])
    date = IsoDateTimeType(required=True)
    value = ModelType(AwardValue, required=True)
    weightedValue = ModelType(AwardValue)
    suppliers = ListType(ModelType(BusinessOrganization, required=True), required=True, min_size=1, max_size=1)
    documents = ListType(ModelType(Document, required=True))
    subcontractingDetails = StringType()

    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()

    complaints = BaseType()
    complaintPeriod = ModelType(Period)


# Negotiation
def validate_lot_id(value):
    tender = get_tender()
    if not value and tender.get("lots"):
        raise ValidationError("This field is required.")
    if value and value not in tuple(lot["id"] for lot in tender.get("lots", "") if lot):
        raise ValidationError("lotID should be one of lots")


class PostNegotiationAward(PostBaseAward):
    lotID = MD5Type()

    def validate_lotID(self, data, value):
        validate_lot_id(value)


class PatchNegotiationAward(PatchBaseAward):
    lotID = MD5Type()

    def validate_lotID(self, data, value):
        if value:
            validate_lot_id(value)


class NegotiationAward(BaseAward):
    lotID = MD5Type()

    def validate_qualified(self, data, value):
        if not value and data["status"] == "active":
            raise ValidationError("Can't update award to active status with not qualified")


# reporting
class PostReportingAward(PostBaseAward):
    suppliers = ListType(ModelType(ContactLessBusinessOrganization, required=True),
                         required=True, min_size=1, max_size=1)
    value = ModelType(Value, required=True)


class PatchReportingAward(PatchBaseAward):
    suppliers = ListType(ModelType(ContactLessBusinessOrganization, required=True),
                         min_size=1, max_size=1)
    value = ModelType(Value)


class ReportingAward(BaseAward):
    suppliers = ListType(ModelType(ContactLessBusinessOrganization, required=True),
                         required=True, min_size=1, max_size=1)
    value = ModelType(Value, required=True)
