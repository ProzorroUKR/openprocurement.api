from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, BooleanType, MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import AmountPercentageValue, Value
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.tender.core.procedure.models.award_milestone import (
    ARMAAwardMilestoneListMixin,
    AwardMilestoneListMixin,
)
from openprocurement.tender.core.procedure.models.base import BaseAward
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.models.item import CDItem, Item
from openprocurement.tender.core.procedure.models.organization import (
    ContactLessSupplier,
    Supplier,
)
from openprocurement.tender.core.procedure.models.req_response import (
    ObjResponseMixin,
    PatchObjResponsesMixin,
)
from openprocurement.tender.core.procedure.models.value import (
    AmountPercentageWeightedValue,
    ESCOValue,
    ESCOWeightedValue,
    WeightedValue,
)


class PostAward(BaseAward):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def date(self):
        return get_request_now().isoformat()

    status = StringType(required=True, choices=["pending"], default="pending")
    value = ModelType(Value)
    weightedValue = ModelType(WeightedValue)
    suppliers = ListType(
        ModelType(Supplier, required=True),
        required=True,
        min_size=1,
        max_size=1,
    )
    items = ListType(ModelType(Item))
    bid_id = MD5Type(required=True)
    lotID = MD5Type()
    complaintPeriod = ModelType(Period)
    subcontractingDetails = StringType()

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
    subcontractingDetails = StringType()


class Award(AwardMilestoneListMixin, ObjResponseMixin, BaseAward):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(required=True, choices=["pending", "unsuccessful", "active", "cancelled"])
    date = IsoDateTimeType(required=True)
    value = ModelType(Value)
    weightedValue = ModelType(WeightedValue)
    suppliers = ListType(
        ModelType(Supplier, required=True),
        required=True,
        min_size=1,
        max_size=1,
    )
    bid_id = MD5Type(required=True)
    lotID = MD5Type()
    complaintPeriod = ModelType(Period)
    subcontractingDetails = StringType()
    complaints = BaseType()
    documents = ListType(ModelType(Document, required=True))
    items = ListType(ModelType(Item))
    period = ModelType(Period)

    qualified = BooleanType()
    eligible = BooleanType()  # qualified/eligible rules: AwardStateMixing.validate_award_qualified_eligible
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


# --- ESCO ---


class ESCOAward(Award):
    value = ModelType(ESCOValue)
    weightedValue = ModelType(ESCOWeightedValue)


class ESCOPostAward(PostAward):
    value = ModelType(ESCOValue)
    weightedValue = ModelType(ESCOWeightedValue)


# --- ARMA (percentage values) ---


class ARMAAward(ARMAAwardMilestoneListMixin, Award):
    weightedValue = ModelType(AmountPercentageWeightedValue)
    value = ModelType(AmountPercentageValue)


class ARMAPostAward(PostAward):
    weightedValue = ModelType(AmountPercentageWeightedValue)
    value = ModelType(AmountPercentageValue)


# --- limited (reporting / negotiation): awards without bids ---


class LimitedAwardValue(Value):
    valueAddedTaxIncluded = BooleanType(required=True, default=lambda: get_tender()["value"]["valueAddedTaxIncluded"])
    currency = StringType(
        required=True,
        max_length=3,
        min_length=3,
        default=lambda: get_tender()["value"]["currency"],
    )


class LimitedPostAward(PostAward):
    bid_id = MD5Type()  # awards are created by the buyer, there are no bids
    qualified = BooleanType()
    eligible = BooleanType()
    value = ModelType(LimitedAwardValue, required=True)
    weightedValue = ModelType(LimitedAwardValue)


class LimitedPatchAward(PatchAward):
    suppliers = ListType(ModelType(Supplier, required=True), min_size=1, max_size=1)
    value = ModelType(LimitedAwardValue)
    lotID = MD5Type()

    def validate_lotID(self, data, value):
        if value:
            tender = get_tender()
            if value not in tuple(lot["id"] for lot in tender.get("lots", "") if lot):
                raise ValidationError("lotID should be one of lots")


class LimitedAward(Award):
    bid_id = MD5Type()
    value = ModelType(LimitedAwardValue, required=True)
    weightedValue = ModelType(LimitedAwardValue)


# reporting: plain value (no defaults from the tender)


class ReportingPostAward(LimitedPostAward):
    suppliers = ListType(
        ModelType(ContactLessSupplier, required=True),
        required=True,
        min_size=1,
        max_size=1,
    )
    value = ModelType(Value, required=True)


class ReportingPatchAward(LimitedPatchAward):
    suppliers = ListType(
        ModelType(ContactLessSupplier, required=True),
        min_size=1,
        max_size=1,
    )
    value = ModelType(Value)


class ReportingAward(LimitedAward):
    suppliers = ListType(
        ModelType(ContactLessSupplier, required=True),
        required=True,
        min_size=1,
        max_size=1,
    )
    value = ModelType(Value, required=True)


# --- competitiveDialogue (stage 2) ---


class CDAward(Award):
    items = ListType(ModelType(CDItem))


class CDPostAward(PostAward):
    items = ListType(ModelType(CDItem))


class CDPatchAward(PatchAward):
    items = ListType(ModelType(CDItem))
