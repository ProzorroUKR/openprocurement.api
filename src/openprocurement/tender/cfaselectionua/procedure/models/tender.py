from decimal import Decimal

from schematics.types import BaseType, StringType
from schematics.types.compound import ListType, ModelType
from schematics.types.serializable import serializable
from schematics.validate import ValidationError

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.validation import validate_features_uniq
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.cfaselectionua.constants import (
    CFA_SELECTION,
    TENDERING_DURATION,
)
from openprocurement.tender.cfaselectionua.procedure.models.agreement import Agreement
from openprocurement.tender.cfaselectionua.procedure.models.feature import Feature
from openprocurement.tender.cfaselectionua.procedure.models.item import Item
from openprocurement.tender.cfaselectionua.procedure.models.lot import (
    Lot,
    PatchTenderLot,
    PostTenderLot,
)
from openprocurement.tender.cfaselectionua.procedure.models.organization import (
    ProcuringEntity,
)
from openprocurement.tender.core.constants import AWARD_CRITERIA_LOWEST_COST
from openprocurement.tender.core.procedure.models.agreement import AgreementUUID
from openprocurement.tender.core.procedure.models.feature import validate_related_items
from openprocurement.tender.core.procedure.models.guarantee import (
    Guarantee,
    PostGuarantee,
)
from openprocurement.tender.core.procedure.models.item import (
    validate_classification_id,
    validate_related_buyer_in_items,
)
from openprocurement.tender.core.procedure.models.lot import validate_lots_uniq
from openprocurement.tender.core.procedure.models.milestone import (
    Milestone,
    validate_milestones_lot,
)
from openprocurement.tender.core.procedure.models.tender import (
    BaseTender,
    PatchBaseTender,
    PostBaseTender,
    validate_items_related_lot,
)
from openprocurement.tender.core.procedure.utils import validate_features_custom_weight
from openprocurement.tender.core.procedure.validation import (
    validate_tender_period_duration,
)


def validate_features(data, features):
    validate_related_items(data, features)
    validate_features_custom_weight(data, features, Decimal("0.3"))


def validate_tender_period(data, period):
    if (
        period
        and period.startDate
        and data.get("enquiryPeriod")
        and data.get("enquiryPeriod").endDate
        and period.startDate < data.get("enquiryPeriod").endDate
    ):
        raise ValidationError("period should begin after enquiryPeriod")
    if period and period.startDate and period.endDate:
        validate_tender_period_duration(data, period, TENDERING_DURATION)


class PostTender(PostBaseTender):
    procurementMethodType = StringType(choices=[CFA_SELECTION], default=CFA_SELECTION)
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST], default=AWARD_CRITERIA_LOWEST_COST)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(choices=["draft"], default="draft")

    agreements = ListType(ModelType(AgreementUUID, required=True), required=True, min_size=1, max_size=1)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    lots = ListType(
        ModelType(PostTenderLot, required=True),
        min_size=1,
        max_size=1,
        required=True,
        validators=[validate_lots_uniq],
    )
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq])
    guarantee = ModelType(PostGuarantee)
    # tenderPeriod = ModelType(PeriodEndRequired)

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    # Not required milestones
    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)

    # def validate_tenderPeriod(self, data, period):
    #     validate_tender_period(data, period)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_features(data, features)


class PatchTender(PatchBaseTender):
    procurementMethodType = StringType(choices=[CFA_SELECTION])
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST])
    procuringEntity = ModelType(ProcuringEntity)
    status = StringType(
        choices=[
            "draft",
            "draft.pending",
            "draft.unsuccessful",
            "active.enquiries",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
            "active.qualification",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ]
    )

    # agreements = ListType(ModelType(Agreement, required=True), min_size=1, max_size=1)
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    lots = ListType(
        ModelType(PatchTenderLot, required=True),
        min_size=1,
        max_size=1,
        validators=[validate_lots_uniq],
    )
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    unsuccessfulReason = ListType(StringType, serialize_when_none=False)
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq])

    tenderPeriod = ModelType(PeriodEndRequired)
    # will be overwritten by serializable
    minimalStep = ModelType(Value)
    guarantee = ModelType(Guarantee)

    def validate_tenderPeriod(self, data, period):
        if period and get_tender()["status"] != "active.enquiries":
            raise ValidationError("Rogue field")


class Tender(BaseTender):
    procurementMethodType = StringType(choices=[CFA_SELECTION], required=True)
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST], required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(
        choices=[
            "draft",
            "draft.pending",
            "draft.unsuccessful",
            "active.enquiries",
            "active.tendering",
            "active.pre-qualification",
            "active.qualification",
        ],
        required=True,
    )

    agreements = ListType(ModelType(Agreement, required=True), required=True, min_size=1, max_size=1)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    lots = ListType(
        ModelType(Lot, required=True),
        min_size=1,
        max_size=1,
        required=True,
        validators=[validate_lots_uniq],
    )
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    unsuccessfulReason = ListType(StringType, serialize_when_none=False)
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq])
    tenderPeriod = ModelType(PeriodEndRequired)
    enquiryPeriod = ModelType(PeriodEndRequired)
    # will be overwritten by serializable
    minimalStep = ModelType(Value)
    value = ModelType(Value)
    guarantee = ModelType(Guarantee)

    next_check = BaseType()

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    # Not required milestones
    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)

    def validate_tenderPeriod(self, data, period):
        validate_tender_period(data, period)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_features(data, features)

    @serializable(
        serialized_name="guarantee",
        serialize_when_none=False,
        type=ModelType(Guarantee),
    )
    def tender_guarantee(self):
        if self.lots:
            lots_amount = [i.guarantee.amount for i in self.lots if i.guarantee]
            if not lots_amount:
                return self.guarantee
            guarantee = {"amount": sum(lots_amount)}
            lots_currency = [i.guarantee.currency for i in self.lots if i.guarantee]
            guarantee["currency"] = lots_currency[0] if lots_currency else None
            if self.guarantee:
                guarantee["currency"] = self.guarantee.currency
            guarantee_class = self._fields["guarantee"]
            return guarantee_class(guarantee)
        else:
            return self.guarantee

    @serializable(serialized_name="minimalStep", type=ModelType(Value, required=False))
    def tender_minimalStep(self):
        return self.minimalStep

    @serializable(serialized_name="value", type=ModelType(Value))
    def tender_value(self):
        return self.value
