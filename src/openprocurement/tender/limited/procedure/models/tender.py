from schematics.types import BaseType, StringType
from schematics.types.compound import ListType, ModelType

from openprocurement.api.constants import (
    MILESTONES_VALIDATION_FROM,
    NEW_NEGOTIATION_CAUSES_FROM,
    QUICK_CAUSE_REQUIRED_FROM,
    TENDER_CAUSE,
)
from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.item import validate_items_uniq
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.validation import ValidationError
from openprocurement.tender.core.procedure.models.item import (
    validate_classification_id,
    validate_related_buyer_in_items,
)
from openprocurement.tender.core.procedure.models.lot import validate_lots_uniq
from openprocurement.tender.core.procedure.models.milestone import (
    Milestone,
    TenderMilestoneTypes,
    validate_milestones_lot,
)
from openprocurement.tender.core.procedure.models.tender import (
    BaseTender,
    PatchBaseTender,
    PostBaseTender,
    validate_items_related_lot,
)
from openprocurement.tender.core.procedure.validation import (
    validate_funders_ids,
    validate_funders_unique,
    validate_milestones,
)
from openprocurement.tender.limited.constants import (
    NEGOTIATION,
    NEGOTIATION_QUICK,
    REPORTING,
)
from openprocurement.tender.limited.procedure.models.item import ReportingItem
from openprocurement.tender.limited.procedure.models.lot import (
    Lot,
    PatchTenderLot,
    PostTenderLot,
)
from openprocurement.tender.limited.procedure.models.organization import (
    NegotiationProcuringEntity,
    ReportFundOrganization,
    ReportingProcuringEntity,
)
from openprocurement.tender.openua.procedure.models.item import Item

VALUE_AMOUNT_THRESHOLD = {
    "goods": 100000,
    "services": 200000,
    "works": 1500000,
}


def reporting_cause_is_required(data, value):
    return all(
        [
            data.get("procuringEntity", {}).get("kind") != "other",
            not data.get("procurementMethodRationale"),
            data.get("value", {}).get("amount", 0) >= VALUE_AMOUNT_THRESHOLD[data["mainProcurementCategory"]],
            not value,
        ]
    )


# reporting
class PostReportingTender(PostBaseTender):
    procurementMethodType = StringType(choices=[REPORTING], default=REPORTING)
    procuringEntity = ModelType(ReportingProcuringEntity, required=True)
    items = ListType(
        ModelType(ReportingItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    value = ModelType(Value)
    status = StringType(choices=["draft"], default="draft")
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq, validate_milestones])

    funders = ListType(
        ModelType(ReportFundOrganization, required=True), validators=[validate_funders_unique, validate_funders_ids]
    )
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)

    def validate_milestones(self, data, value):
        if value:
            for milestone in value:
                if milestone.type == TenderMilestoneTypes.DELIVERY.value:
                    raise ValidationError(f"Forbidden to add milestone with type {TenderMilestoneTypes.DELIVERY.value}")

    def validate_cause(self, data, value):
        if reporting_cause_is_required(data, value):
            raise ValidationError(BaseType.MESSAGES["required"])

        if value is not None and value not in TENDER_CAUSE:
            raise ValidationError(f"Value must be one of ['{TENDER_CAUSE}'].")


class PatchReportingTender(PatchBaseTender):
    procurementMethodType = StringType(choices=[REPORTING])
    procuringEntity = ModelType(ReportingProcuringEntity)
    items = ListType(
        ModelType(ReportingItem, required=True),
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    value = ModelType(Value)
    status = StringType(choices=["draft", "active"])
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq, validate_milestones])

    funders = ListType(
        ModelType(ReportFundOrganization, required=True), validators=[validate_funders_unique, validate_funders_ids]
    )
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()


class ReportingTender(BaseTender):
    procurementMethodType = StringType(choices=[REPORTING], required=True)
    procuringEntity = ModelType(ReportingProcuringEntity, required=True)
    items = ListType(
        ModelType(ReportingItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    value = ModelType(Value)
    status = StringType(choices=["draft", "active", "complete", "cancelled", "unsuccessful"])
    awards = BaseType()
    # contracts = BaseType()
    cancellations = BaseType()

    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq, validate_milestones])
    funders = ListType(
        ModelType(ReportFundOrganization, required=True), validators=[validate_funders_unique, validate_funders_ids]
    )
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)

    def validate_milestones(self, data, value):
        if value:
            for milestone in value:
                if milestone.type == TenderMilestoneTypes.DELIVERY.value:
                    raise ValidationError(f"Forbidden to add milestone with type {TenderMilestoneTypes.DELIVERY.value}")

    def validate_cause(self, data, value):
        if reporting_cause_is_required(data, value):
            raise ValidationError(BaseType.MESSAGES["required"])

        if value is not None and value not in TENDER_CAUSE:
            raise ValidationError(f"Value must be one of ['{TENDER_CAUSE}'].")


# Negotiation

basic_cause_choices = [
    "twiceUnsuccessful",
    "additionalPurchase",
    "additionalConstruction",
    "stateLegalServices",
]

cause_choices = [
    "artContestIP",
    "noCompetition",
] + basic_cause_choices

cause_choices_new = [
    "resolvingInsolvency",
    "artPurchase",
    "contestWinner",
    "technicalReasons",
    "intProperty",
    "lastHope",
] + basic_cause_choices


def validate_cause(value):
    is_new = get_first_revision_date(get_tender(), default=get_now()) > NEW_NEGOTIATION_CAUSES_FROM
    choices = cause_choices_new if is_new else cause_choices
    if value not in choices:
        raise ValidationError("Value must be one of ['{}'].".format("', '".join(choices)))


class PostNegotiationTender(PostBaseTender):
    procurementMethodType = StringType(choices=[NEGOTIATION], default=NEGOTIATION)
    procuringEntity = ModelType(NegotiationProcuringEntity, required=True)
    status = StringType(choices=["draft"], default="draft")
    value = ModelType(Value, required=True)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    cause = StringType(required=True)
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDescription_ru = StringType()
    lots = ListType(ModelType(PostTenderLot, required=True), validators=[validate_lots_uniq])

    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq, validate_milestones])

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_cause(self, data, value):
        validate_cause(value)

    def validate_milestones(self, data, value):
        required = get_first_revision_date(get_tender(), default=get_now()) > MILESTONES_VALIDATION_FROM
        if required and (value is None or len(value) < 1):
            raise ValidationError("Tender should contain at least one milestone")

        validate_milestones_lot(data, value)


class PatchNegotiationTender(PatchBaseTender):
    procurementMethodType = StringType(choices=[NEGOTIATION])
    procuringEntity = ModelType(NegotiationProcuringEntity)
    status = StringType(choices=["draft", "active"])
    value = ModelType(Value)
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDescription_ru = StringType()
    lots = ListType(ModelType(PatchTenderLot, required=True), validators=[validate_lots_uniq])

    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq, validate_milestones])


class NegotiationTender(BaseTender):
    procurementMethodType = StringType(choices=[NEGOTIATION], required=True)
    procuringEntity = ModelType(NegotiationProcuringEntity, required=True)
    status = StringType(choices=["draft", "active", "complete", "cancelled", "unsuccessful"])
    value = ModelType(Value, required=True)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    cause = StringType(required=True)
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDescription_ru = StringType()
    lots = ListType(ModelType(Lot, required=True), validators=[validate_lots_uniq])

    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq, validate_milestones])
    awards = BaseType()

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_cause(self, data, value):
        validate_cause(value)

    def validate_milestones(self, data, value):
        required = get_first_revision_date(get_tender(), default=get_now()) > MILESTONES_VALIDATION_FROM
        if required and (value is None or len(value) < 1):
            raise ValidationError("Tender should contain at least one milestone")
        validate_milestones_lot(data, value)


# Negotiation Quick
cause_choices_quick = cause_choices + ["quick"]
cause_choices_quick_new = cause_choices_new + [
    "emergency",
    "humanitarianAid",
    "contractCancelled",
    "activeComplaint",
]


def validate_cause_quick(value):
    required = get_first_revision_date(get_tender(), default=get_now()) >= QUICK_CAUSE_REQUIRED_FROM
    if required and not value:
        raise ValidationError(BaseType.MESSAGES["required"])

    if value:
        is_new = get_first_revision_date(get_tender(), default=get_now()) > NEW_NEGOTIATION_CAUSES_FROM
        choices = cause_choices_quick_new if is_new else cause_choices_quick
        if value not in choices:
            raise ValidationError("Value must be one of ['{}'].".format("', '".join(choices)))


class PostNegotiationQuickTender(PostNegotiationTender):
    procurementMethodType = StringType(choices=[NEGOTIATION_QUICK], default=NEGOTIATION_QUICK)
    cause = StringType()

    def validate_cause(self, data, value):
        validate_cause_quick(value)


class PatchNegotiationQuickTender(PatchNegotiationTender):
    procurementMethodType = StringType(choices=[NEGOTIATION_QUICK])


class NegotiationQuickTender(NegotiationTender):
    procurementMethodType = StringType(choices=[NEGOTIATION_QUICK], required=True)
    cause = StringType()

    def validate_cause(self, data, value):
        validate_cause_quick(value)
