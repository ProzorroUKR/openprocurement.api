from datetime import datetime
from decimal import Decimal
from typing import Literal

from isodate import duration_isoformat
from pydantic import Field, field_validator

from openprocurement.api.constants import TENDER_CAUSE, ProcurementMethodType
from openprocurement.api.constants_env import (
    NEW_NEGOTIATION_CAUSES_FROM,
)
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model, model_field_validator, validate_uniq_code, validate_uniq_id
from openprocurement.api.procedure.models.milestone import Milestone
from openprocurement.api.procedure.models.period import Period, PeriodEndRequired
from openprocurement.api.procedure.models.value import EstimatedValue
from openprocurement.api.utils import get_first_revision_date
from openprocurement.tender.cfaua.constants import CFA_UA_MAX_AGREEMENT_PERIOD
from openprocurement.tender.cfaua.constants import CFA_UA_MIN_BIDS_NUMBER as CFA_MIN_BIDS_NUMBER
from openprocurement.tender.core.constants import (
    AwardCriteria,
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
from openprocurement.tender.core.procedure.models.milestone import validate_milestones_lot
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
from openprocurement.tender.limited.constants import cause_choices as NEGOTIATION_CAUSE_CHOICES
from openprocurement.tender.limited.constants import cause_choices_new as NEGOTIATION_CAUSE_CHOICES_NEW
from openprocurement.tender.limited.constants import cause_choices_quick as NEGOTIATION_QUICK_CAUSE_CHOICES
from openprocurement.tender.limited.constants import cause_choices_quick_new as NEGOTIATION_QUICK_CAUSE_CHOICES_NEW
from openprocurement.tender.open.constants import OpenProcurementMethodType


def validate_award_period(tender, period):
    auction_period = getattr(tender, "auctionPeriod", None)  # not a field of all the tenders
    if (
        period
        and period.startDate
        and auction_period
        and auction_period.endDate
        and period.startDate < auction_period.endDate
    ):
        raise ValidationError("period should begin after auctionPeriod")
    if (
        period
        and period.startDate
        and tender.tenderPeriod
        and tender.tenderPeriod.endDate
        and period.startDate < tender.tenderPeriod.endDate
    ):
        raise ValidationError("period should begin after tenderPeriod")


class PatchTenderMilestonesMixin(Model):
    milestones: list[Milestone] | None = None

    @field_validator("milestones")
    @classmethod
    def validate_milestones_items(cls, value):
        validate_uniq_id(value)
        return value


class TenderMilestonesMixin(Model):
    """
    milestones relation to lots; whether milestones are required (and which types)
    is validated in TenderDetailsState (milestones_required, milestones_delivery_financing_required)
    """

    milestones: list[Milestone] | None = None

    @model_field_validator("milestones")
    def validate_milestones(self, value):
        validate_milestones_lot(self, value)

    @field_validator("milestones")
    @classmethod
    def validate_milestones_items(cls, value):
        validate_uniq_id(value)
        return value


class TenderSubmissionMixin(Model):
    submissionMethod: Literal["electronicAuction"] | None = None
    submissionMethodDetails: str | None = None
    submissionMethodDetails_en: str | None = None
    submissionMethodDetails_ru: str | None = None


class TenderGuaranteeMixin(Model):
    guarantee: BasicValue | None = None


class PostTenderPeriodsMixin(Model):
    enquiryPeriod: EnquiryPeriod | None = None
    tenderPeriod: PeriodEndRequired
    awardPeriod: Period | None = None
    auctionPeriod: Period | None = None

    @model_field_validator("awardPeriod")
    def validate_award_period(self, period):
        validate_award_period(self, period)


class PatchTenderPeriodsMixin(Model):
    enquiryPeriod: EnquiryPeriod | None = None
    tenderPeriod: PeriodEndRequired | None = None
    awardPeriod: Period | None = None


class TenderPeriodsMixin(Model):
    enquiryPeriod: EnquiryPeriod | None = None
    tenderPeriod: PeriodEndRequired
    awardPeriod: Period | None = None
    auctionPeriod: TenderAuctionPeriod | None = None

    @model_field_validator("awardPeriod")
    def validate_award_period(self, period):
        validate_award_period(self, period)


class PostTenderItemsMixin(Model):
    items: list[Item] | None = Field(None, min_length=1)

    @model_field_validator("items")
    def validate_items(self, items):
        validate_related_buyer_in_items(self, items)

    @field_validator("items")
    @classmethod
    def validate_items_items(cls, value):
        validate_uniq_id(value)
        return value


class PatchTenderItemsMixin(Model):
    items: list[Item] | None = Field(None, min_length=1)

    @field_validator("items")
    @classmethod
    def validate_items_items(cls, value):
        validate_uniq_id(value)
        return value


class TenderItemsMixin(Model):
    items: list[Item] | None = Field(None, min_length=1)

    @model_field_validator("items")
    def validate_items(self, items):
        validate_related_buyer_in_items(self, items)

    @field_validator("items")
    @classmethod
    def validate_items_items(cls, value):
        validate_uniq_id(value)
        return value


class PatchTenderFeaturesMixin(Model):
    features: list[Feature] | None = None

    @field_validator("features")
    @classmethod
    def validate_features_items(cls, value):
        validate_uniq_code(value)
        return value


class TenderFeaturesMixin(Model):
    features: list[Feature] | None = None

    @model_field_validator("features")
    def validate_features(self, features):
        validate_related_items(self, features)

    @field_validator("features")
    @classmethod
    def validate_features_items(cls, value):
        validate_uniq_code(value)
        return value


class PostTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PostTenderPeriodsMixin,
    PostTenderItemsMixin,
    TenderFeaturesMixin,
    TenderMilestonesMixin,
    PostBaseTender,
):
    procurementMethodType: OpenProcurementMethodType = ProcurementMethodType.BELOW_THRESHOLD
    awardCriteria: AwardCriteria | None = None
    procuringEntity: ProcuringEntity
    value: PostEstimatedValue
    minimalStep: PostEstimatedValue | None = None
    lots: list[PostTenderLot] | None = None
    targets: list[PostMetric] | None = None

    @field_validator("lots")
    @classmethod
    def validate_lots(cls, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")
        return value

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value

    @field_validator("targets")
    @classmethod
    def validate_targets_items(cls, value):
        validate_uniq_id(value)
        validate_observation_ids_uniq(value)
        return value


class PatchTender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    PatchTenderPeriodsMixin,
    PatchTenderItemsMixin,
    PatchTenderFeaturesMixin,
    PatchTenderMilestonesMixin,
    PatchBaseTender,
):
    awardCriteria: AwardCriteria | None = None
    procuringEntity: ProcuringEntity | None = None
    value: PostEstimatedValue | None = None
    minimalStep: PostEstimatedValue | None = None
    lots: list[PatchTenderLot] | None = None
    targets: list[Metric] | None = None

    @field_validator("lots")
    @classmethod
    def validate_lots(cls, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")
        return value

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value

    @field_validator("targets")
    @classmethod
    def validate_targets_items(cls, value):
        validate_uniq_id(value)
        validate_observation_ids_uniq(value)
        return value


class Tender(
    TenderSubmissionMixin,
    TenderGuaranteeMixin,
    TenderPeriodsMixin,
    TenderItemsMixin,
    TenderFeaturesMixin,
    TenderMilestonesMixin,
    BaseTender,
):
    procurementMethodType: OpenProcurementMethodType
    awardCriteria: AwardCriteria
    procuringEntity: ProcuringEntity
    value: PostEstimatedValue
    minimalStep: PostEstimatedValue | None = None
    lots: list[Lot] | None = None
    targets: list[Metric] | None = None

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value

    @field_validator("targets")
    @classmethod
    def validate_targets_items(cls, value):
        validate_uniq_id(value)
        validate_observation_ids_uniq(value)
        return value


class PatchDraftTender(PatchTender):
    inspector: Organization | None = None


class PatchActiveTender(Model):
    """
    Fields allowed to be changed in active.tendering (belowThreshold, requestForProposal)
    """

    tenderPeriod: PeriodEndRequired | None = None
    guarantee: BasicValue | None = None
    value: EstimatedValue | None = None
    milestones: list[Milestone] | None = None
    items: list[Item] | None = Field(None, min_length=1)
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    documents: list[PostDocument] | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    mainProcurementCategory: str | None = None
    lots: list[PatchTenderLot] | None = None
    contractTemplateName: str | None = None

    @field_validator("milestones")
    @classmethod
    def validate_milestones_items(cls, value):
        validate_uniq_id(value)
        return value

    @field_validator("items")
    @classmethod
    def validate_items_items(cls, value):
        validate_uniq_id(value)
        return value

    @field_validator("lots")
    @classmethod
    def validate_lots_items(cls, value):
        validate_uniq_id(value)
        return value


def validate_esco_yearly_payments_percentage_range(tender, value):
    if not value:  # for tender with lots this field is rogue in tender and can be empty
        return
    if tender.fundingKind == "other" and value != Decimal("0.8"):
        raise ValidationError("when fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8")
    if tender.fundingKind == "budget" and (value > Decimal("0.8") or value < Decimal("0")):
        raise ValidationError(
            "when fundingKind is budget, yearlyPaymentsPercentageRange should be less or equal 0.8, and more or equal 0"
        )


def validate_esco_lots_yearly_payments_percentage_range(tender, lots):
    if lots:
        if tender.fundingKind == "other":
            for lot in lots:
                if lot.yearlyPaymentsPercentageRange != Decimal("0.8"):
                    raise ValidationError(
                        "when tender fundingKind is other, yearlyPaymentsPercentageRange should be equal 0.8"
                    )
        elif tender.fundingKind == "budget":
            for lot in lots:
                value = lot.yearlyPaymentsPercentageRange
                if value > Decimal("0.8") or value < Decimal("0"):
                    raise ValidationError(
                        "when tender fundingKind is budget, "
                        "yearlyPaymentsPercentageRange should be less or equal 0.8, and more or equal 0"
                    )


def validate_cfa_features(data, features):
    validate_related_items(data, features)
    if features:
        for i in features:
            if i.featureOf == "lot":
                raise ValidationError("Features are not allowed for lots")


def validate_cfa_max_awards_number(number, *args):
    if number is not None and number < CFA_MIN_BIDS_NUMBER:
        raise ValidationError("Maximal awards number can't be less then minimal bids number")


def validate_cfa_max_agreement_duration_period(value):
    date = datetime(1, 1, 1)
    if value is not None and (date + value) > (date + CFA_UA_MAX_AGREEMENT_PERIOD):
        raise ValidationError(
            "Agreement duration period is greater than {}".format(duration_isoformat(CFA_UA_MAX_AGREEMENT_PERIOD))
        )


def validate_reporting_cause(value):
    if value is not None and value not in TENDER_CAUSE:
        raise ValidationError(f"Value must be one of ['{TENDER_CAUSE}'].")


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


def validate_cd_shortlisted_firm_ids(tender, firms):
    lot_ids = {lot.id for lot in tender.lots or []}
    for f in firms:
        for lot in f.lots or []:
            lot_id = lot.id
            if lot_id and lot_id not in lot_ids:
                raise ValidationError("id should be one of lots")
