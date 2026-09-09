from datetime import datetime
from decimal import Decimal

from isodate import duration_isoformat
from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.constants import TENDER_CAUSE
from openprocurement.api.constants_env import (
    NEW_NEGOTIATION_CAUSES_FROM,
)
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period, PeriodEndRequired
from openprocurement.api.procedure.models.value import EstimatedValue
from openprocurement.api.procedure.types import ListType
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.validation import validate_uniq_code, validate_uniq_id
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.cfaua.constants import (
    MAX_AGREEMENT_PERIOD,
)
from openprocurement.tender.cfaua.constants import (
    MIN_BIDS_NUMBER as CFA_MIN_BIDS_NUMBER,
)
from openprocurement.tender.core.constants import (
    AWARD_CRITERIA_CHOICES,
    CORE_TENDER_PROCUREMENT_METHOD_TYPES,
)
from openprocurement.tender.core.procedure.models.document import PostDocument
from openprocurement.tender.core.procedure.models.feature import (
    Feature,
    validate_related_items,
)
from openprocurement.tender.core.procedure.models.item import (
    Item,
    validate_related_buyer_in_items,
)
from openprocurement.tender.core.procedure.models.lot import (
    Lot,
    PatchTenderLot,
    PostTenderLot,
)
from openprocurement.tender.core.procedure.models.metric import (
    Metric,
    PostMetric,
    validate_observation_ids_uniq,
)
from openprocurement.tender.core.procedure.models.milestone import (
    Milestone,
    validate_milestones_lot,
)
from openprocurement.tender.core.procedure.models.organization import (
    Organization,
    ProcuringEntity,
)
from openprocurement.tender.core.procedure.models.period import (
    EnquiryPeriod,
    TenderAuctionPeriod,
)
from openprocurement.tender.core.procedure.models.tender_base import (
    BaseTender,
    PatchBaseTender,
    PostBaseTender,
)
from openprocurement.tender.core.procedure.models.value import (
    BasicValue,
    PostEstimatedValue,
)
from openprocurement.tender.limited.constants import (
    cause_choices as NEGOTIATION_CAUSE_CHOICES,
)
from openprocurement.tender.limited.constants import (
    cause_choices_new as NEGOTIATION_CAUSE_CHOICES_NEW,
)
from openprocurement.tender.limited.constants import (
    cause_choices_quick as NEGOTIATION_QUICK_CAUSE_CHOICES,
)
from openprocurement.tender.limited.constants import (
    cause_choices_quick_new as NEGOTIATION_QUICK_CAUSE_CHOICES_NEW,
)


def validate_items_related_lot(data, items):
    related_lots = {i["relatedLot"] for i in items if i.get("relatedLot")}

    if related_lots:
        lot_ids = {lot["id"] for lot in data.get("lots") or []}
        if related_lots - lot_ids:
            raise ValidationError([{"relatedLot": ["relatedLot should be one of lots"]}])


def validate_award_period(data, period):
    if (
        period
        and period.startDate
        and data.get("auctionPeriod")
        and data["auctionPeriod"].get("endDate")
        and period.startDate < data["auctionPeriod"]["endDate"]
    ):
        raise ValidationError("period should begin after auctionPeriod")
    if (
        period
        and period.startDate
        and data.get("tenderPeriod")
        and data["tenderPeriod"].get("endDate")
        and period.startDate < data["tenderPeriod"]["endDate"]
    ):
        raise ValidationError("period should begin after tenderPeriod")


class PatchTenderMilestonesMixin(Model):
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_uniq_id])


class TenderMilestonesMixin(Model):
    """
    milestones relation to lots; whether milestones are required (and which types)
    is validated in TenderDetailsState (milestones_required, milestones_delivery_financing_required)
    """

    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_uniq_id])

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)


class TenderSubmissionMixin(Model):
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()


class TenderGuaranteeMixin(Model):
    guarantee = ModelType(BasicValue)


class PostTenderPeriodsMixin(Model):
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    auctionPeriod = ModelType(Period)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)


class PatchTenderPeriodsMixin(Model):
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired)
    awardPeriod = ModelType(Period)


class TenderPeriodsMixin(Model):
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    auctionPeriod = ModelType(TenderAuctionPeriod)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)


class PostTenderItemsMixin(Model):
    _items_related_lot_check = True  # reporting: relatedLot availability is reported by the state

    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        if self._items_related_lot_check:
            validate_items_related_lot(data, items)


class PatchTenderItemsMixin(Model):
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_uniq_id],
    )


class TenderItemsMixin(Model):
    _items_related_lot_check = True

    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        if self._items_related_lot_check:
            validate_items_related_lot(data, items)


class PatchTenderFeaturesMixin(Model):
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])


class TenderFeaturesMixin(Model):
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])

    def validate_features(self, data, features):
        validate_related_items(data, features)


class PostTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PostTenderPeriodsMixin,
    PostTenderItemsMixin,
    TenderFeaturesMixin,
    TenderMilestonesMixin,
    PostBaseTender,
):
    procurementMethodType = StringType(choices=CORE_TENDER_PROCUREMENT_METHOD_TYPES, default=BELOW_THRESHOLD)
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES)

    procuringEntity = ModelType(ProcuringEntity, required=True)
    value = ModelType(PostEstimatedValue, required=True)
    minimalStep = ModelType(PostEstimatedValue)
    lots = ListType(ModelType(PostTenderLot, required=True), validators=[validate_uniq_id])
    targets = ListType(
        ModelType(PostMetric),
        validators=[validate_uniq_id, validate_observation_ids_uniq],
    )

    def validate_lots(self, data, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")


class PatchTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PatchTenderPeriodsMixin,
    PatchTenderItemsMixin,
    PatchTenderFeaturesMixin,
    PatchTenderMilestonesMixin,
    PatchBaseTender,
):
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES)
    procuringEntity = ModelType(ProcuringEntity)
    value = ModelType(PostEstimatedValue)
    minimalStep = ModelType(PostEstimatedValue)
    lots = ListType(ModelType(PatchTenderLot, required=True), validators=[validate_uniq_id])
    targets = ListType(
        ModelType(Metric),
        validators=[validate_uniq_id, validate_observation_ids_uniq],
    )

    def validate_lots(self, data, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")


class Tender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    TenderPeriodsMixin,
    TenderItemsMixin,
    TenderFeaturesMixin,
    TenderMilestonesMixin,
    BaseTender,
):
    procurementMethodType = StringType(choices=CORE_TENDER_PROCUREMENT_METHOD_TYPES, required=True)
    awardCriteria = StringType(choices=AWARD_CRITERIA_CHOICES, required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    value = ModelType(PostEstimatedValue, required=True)
    minimalStep = ModelType(PostEstimatedValue)
    lots = ListType(ModelType(Lot, required=True), validators=[validate_uniq_id])

    targets = ListType(
        ModelType(Metric),
        validators=[validate_uniq_id, validate_observation_ids_uniq],
    )


class PatchDraftTender(PatchTender):
    inspector = ModelType(Organization)


class PatchActiveTender(Model):
    """
    Fields allowed to be changed in active.tendering (belowThreshold, requestForProposal)
    """

    tenderPeriod = ModelType(PeriodEndRequired)
    guarantee = ModelType(BasicValue)
    value = ModelType(EstimatedValue)
    milestones = ListType(
        ModelType(Milestone, required=True),
        validators=[validate_uniq_id],
    )
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_uniq_id],
    )
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    documents = ListType(ModelType(PostDocument, required=True))
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    mainProcurementCategory = StringType()  # choices are validated in state
    lots = ListType(ModelType(PatchTenderLot, required=True), validators=[validate_uniq_id])
    contractTemplateName = StringType()


# --- ESCO ---


def validate_esco_yearly_payments_percentage_range(data, value):
    if not value:  # for tender with lots this field is rogue in tender and can be empty
        return
    if data["fundingKind"] == "other" and value != Decimal("0.8"):
        raise ValidationError("when fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8")
    if data["fundingKind"] == "budget" and (value > Decimal("0.8") or value < Decimal("0")):
        raise ValidationError(
            "when fundingKind is budget, yearlyPaymentsPercentageRange should be less or equal 0.8, and more or equal 0"
        )


def validate_esco_lots_yearly_payments_percentage_range(data, lots):
    if lots:
        if data["fundingKind"] == "other":
            for lot in lots:
                if lot["yearlyPaymentsPercentageRange"] != Decimal("0.8"):
                    raise ValidationError(
                        "when tender fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8"
                    )
        elif data["fundingKind"] == "budget":
            for lot in lots:
                value = lot["yearlyPaymentsPercentageRange"]
                if value > Decimal("0.8") or value < Decimal("0"):
                    raise ValidationError(
                        "when tender fundingKind is budget, "
                        "yearlyPaymentsPercentageRange should be less or equal 0.8, and more or equal 0"
                    )


# --- CFA (closeFrameworkAgreementUA) ---


def validate_cfa_features(data, features):
    validate_related_items(data, features)
    if features:
        for i in features:
            if i.featureOf == "lot":
                raise ValidationError("Features are not allowed for lots")


def validate_cfa_max_awards_number(number, *args):
    if number < CFA_MIN_BIDS_NUMBER:
        raise ValidationError("Maximal awards number can't be less then minimal bids number")


def validate_cfa_max_agreement_duration_period(value):
    date = datetime(1, 1, 1)
    if (date + value) > (date + MAX_AGREEMENT_PERIOD):
        raise ValidationError(
            "Agreement duration period is greater than {}".format(duration_isoformat(MAX_AGREEMENT_PERIOD))
        )

    # Non-required mainProcurementCategory
    # Not required milestones


# --- limited: reporting ---


def validate_reporting_cause(value):
    if value is not None and value not in TENDER_CAUSE:
        raise ValidationError(f"Value must be one of ['{TENDER_CAUSE}'].")


# --- limited: negotiation / negotiation.quick ---


def validate_negotiation_cause(value):
    is_new = get_first_revision_date(get_tender(), default=get_request_now()) > NEW_NEGOTIATION_CAUSES_FROM
    choices = NEGOTIATION_CAUSE_CHOICES_NEW if is_new else NEGOTIATION_CAUSE_CHOICES
    if value is not None and value not in choices:
        raise ValidationError("Value must be one of ['{}'].".format("', '".join(choices)))


def validate_negotiation_quick_cause(value):
    if value:
        is_new = get_first_revision_date(get_tender(), default=get_request_now()) > NEW_NEGOTIATION_CAUSES_FROM
        choices = NEGOTIATION_QUICK_CAUSE_CHOICES_NEW if is_new else NEGOTIATION_QUICK_CAUSE_CHOICES
        if value not in choices:
            raise ValidationError("Value must be one of ['{}'].".format("', '".join(choices)))


def validate_cd_shortlisted_firm_ids(data, firms):
    lot_ids = {e["id"] for e in data.get("lots") or ""}
    for f in firms:
        for lot in f.get("lots") or "":
            lot_id = lot.get("id")
            if lot_id and lot_id not in lot_ids:
                raise ValidationError("id should be one of lots")

    # Non-required mainProcurementCategory
