from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, BooleanType, MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.tender.core.procedure.models.award_milestone import (
    AwardMilestoneListMixin,
)
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.models.organization import (
    BusinessOrganization,
    ContactLessBusinessOrganization,
)


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
    eligible = BooleanType()
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


class BaseAward(AwardMilestoneListMixin, Model):
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
    period = ModelType(Period)

    def validate_qualified(self, data, qualified):
        if data["status"] == "active" and not qualified:
            raise ValidationError("Can't update award to active status with not qualified")
        if data["status"] == "unsuccessful" and (
            qualified is None
            or (hasattr(self, "eligible") and data.get("eligible") is None)
            or (qualified and (not hasattr(self, "eligible") or data["eligible"]))
        ):
            raise ValidationError(
                "Can't update award to unsuccessful status when qualified/eligible isn't set to False"
            )


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


# reporting
class PostReportingAward(PostBaseAward):
    suppliers = ListType(
        ModelType(ContactLessBusinessOrganization, required=True), required=True, min_size=1, max_size=1
    )
    value = ModelType(Value, required=True)


class PatchReportingAward(PatchBaseAward):
    suppliers = ListType(ModelType(ContactLessBusinessOrganization, required=True), min_size=1, max_size=1)
    value = ModelType(Value)


class ReportingAward(BaseAward):
    suppliers = ListType(
        ModelType(ContactLessBusinessOrganization, required=True), required=True, min_size=1, max_size=1
    )
    value = ModelType(Value, required=True)
