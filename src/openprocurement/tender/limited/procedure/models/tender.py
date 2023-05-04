from schematics.types import StringType, BaseType
from schematics.types.compound import ModelType, ListType
from openprocurement.api.constants import (
    MILESTONES_VALIDATION_FROM,
    NEW_NEGOTIATION_CAUSES_FROM,
    QUICK_CAUSE_REQUIRED_FROM,
)
from openprocurement.api.validation import ValidationError
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.models import Value
from openprocurement.tender.core.validation import validate_milestones
from openprocurement.tender.core.models import validate_funders_unique, validate_funders_ids
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.models.tender import (
    PostBaseTender,
    PatchBaseTender,
    BaseTender,
)
from openprocurement.tender.core.procedure.models.milestone import Milestone, validate_milestones_lot
from openprocurement.tender.core.procedure.models.lot import validate_lots_uniq
from openprocurement.tender.core.procedure.models.tender import validate_items_related_lot
from openprocurement.tender.core.procedure.models.item import (
    validate_cpv_group,
    validate_classification_id,
    validate_items_uniq,
    validate_related_buyer_in_items,
)
from openprocurement.tender.openua.procedure.models.item import Item
from openprocurement.tender.limited.procedure.models.item import ReportingItem
from openprocurement.tender.limited.procedure.models.lot import PostTenderLot, PatchTenderLot, Lot
from openprocurement.tender.limited.procedure.models.organization import (
    ReportingProcuringEntity,
    NegotiationProcuringEntity,
    ReportFundOrganization,
)
from openprocurement.tender.limited.constants import REPORTING, NEGOTIATION, NEGOTIATION_QUICK


# reporting
class PostReportingTender(PostBaseTender):
    procurementMethodType = StringType(choices=[REPORTING], default=REPORTING)
    procuringEntity = ModelType(ReportingProcuringEntity, required=True)
    items = ListType(
        ModelType(ReportingItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )
    value = ModelType(Value)
    procurementMethod = StringType(choices=["limited"], default="limited")
    status = StringType(choices=["draft"], default="draft")
    milestones = ListType(ModelType(Milestone, required=True),
                          validators=[validate_items_uniq, validate_milestones])

    funders = ListType(
        ModelType(ReportFundOrganization, required=True),
        validators=[validate_funders_unique, validate_funders_ids]
    )

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)


class PatchReportingTender(PatchBaseTender):
    procurementMethodType = StringType(choices=[REPORTING])
    procuringEntity = ModelType(ReportingProcuringEntity)
    items = ListType(
        ModelType(ReportingItem, required=True),
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )
    value = ModelType(Value)
    procurementMethod = StringType(choices=["limited"])
    status = StringType(choices=["draft", "active"])
    milestones = ListType(ModelType(Milestone, required=True),
                          validators=[validate_items_uniq, validate_milestones])

    funders = ListType(
        ModelType(ReportFundOrganization, required=True),
        validators=[validate_funders_unique, validate_funders_ids]
    )


class ReportingTender(BaseTender):
    procurementMethodType = StringType(choices=[REPORTING], required=True)
    procuringEntity = ModelType(ReportingProcuringEntity, required=True)
    items = ListType(
        ModelType(ReportingItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )
    value = ModelType(Value)
    procurementMethod = StringType(choices=["limited"], required=True)
    status = StringType(
        choices=[
            "draft",
            "active",
            "complete",
            "cancelled",
            "unsuccessful"
        ]
    )
    awards = BaseType()
    # contracts = BaseType()
    cancellations = BaseType()

    milestones = ListType(ModelType(Milestone, required=True),
                          validators=[validate_items_uniq, validate_milestones])
    funders = ListType(
        ModelType(ReportFundOrganization, required=True),
        validators=[validate_funders_unique, validate_funders_ids]
    )

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)


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
    "lastHope"
] + basic_cause_choices


def validate_cause(value):
    is_new = get_first_revision_date(get_tender(), default=get_now()) > NEW_NEGOTIATION_CAUSES_FROM
    choices = cause_choices_new if is_new else cause_choices
    if value not in choices:
        raise ValidationError("Value must be one of ['{}'].".format("', '".join(choices)))


class PostNegotiationTender(PostBaseTender):
    procurementMethodType = StringType(choices=[NEGOTIATION], default=NEGOTIATION)
    procurementMethod = StringType(choices=["limited"], default="limited")
    procuringEntity = ModelType(NegotiationProcuringEntity, required=True)
    status = StringType(choices=["draft"], default="draft")
    value = ModelType(Value, required=True)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )
    cause = StringType(required=True)
    causeDescription = StringType(required=True, min_length=1)
    causeDescription_en = StringType(min_length=1)
    causeDescription_ru = StringType(min_length=1)
    lots = ListType(ModelType(PostTenderLot, required=True), validators=[validate_lots_uniq])

    milestones = ListType(ModelType(Milestone, required=True),
                          validators=[validate_items_uniq, validate_milestones])

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
    procurementMethod = StringType(choices=["limited"])
    procuringEntity = ModelType(NegotiationProcuringEntity)
    status = StringType(choices=["draft", "active"])
    value = ModelType(Value)
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )
    cause = StringType()
    causeDescription = StringType(min_length=1)
    causeDescription_en = StringType(min_length=1)
    causeDescription_ru = StringType(min_length=1)
    lots = ListType(ModelType(PatchTenderLot, required=True), validators=[validate_lots_uniq])

    milestones = ListType(ModelType(Milestone, required=True),
                          validators=[validate_items_uniq, validate_milestones])


class NegotiationTender(BaseTender):
    procurementMethodType = StringType(choices=[NEGOTIATION], required=True)
    procurementMethod = StringType(choices=["limited"], required=True)
    procuringEntity = ModelType(NegotiationProcuringEntity, required=True)
    status = StringType(
        choices=[
            "draft",
            "active",
            "complete",
            "cancelled",
            "unsuccessful"
        ]
    )
    value = ModelType(Value, required=True)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )
    cause = StringType(required=True)
    causeDescription = StringType(required=True, min_length=1)
    causeDescription_en = StringType(min_length=1)
    causeDescription_ru = StringType(min_length=1)
    lots = ListType(ModelType(Lot, required=True), validators=[validate_lots_uniq])

    milestones = ListType(ModelType(Milestone, required=True),
                          validators=[validate_items_uniq, validate_milestones])
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
