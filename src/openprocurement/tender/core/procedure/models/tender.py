from datetime import datetime
from decimal import Decimal

from isodate import duration_isoformat
from schematics.exceptions import ValidationError
from schematics.types import BaseType, IntType, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.constants import TENDER_CAUSE
from openprocurement.api.constants_env import (
    MILESTONES_VALIDATION_FROM,
    NEW_NEGOTIATION_CAUSES_FROM,
    REQUIRED_DELIVERY_AND_FINANCING_MILESTONES_VALIDATION_FROM,
)
from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.models.item import Classification
from openprocurement.api.procedure.models.period import Period, PeriodEndRequired
from openprocurement.api.procedure.models.value import EstimatedValue, Value
from openprocurement.api.procedure.types import DecimalType, IsoDurationType, ListType
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.validation import validate_uniq_code, validate_uniq_id
from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.cfaselectionua.constants import CFA_SELECTION
from openprocurement.tender.cfaua.constants import (
    CFA_UA,
    MAX_AGREEMENT_PERIOD,
)
from openprocurement.tender.cfaua.constants import (
    LOTS_MAX_SIZE as CFA_LOTS_MAX_SIZE,
)
from openprocurement.tender.cfaua.constants import (
    LOTS_MIN_SIZE as CFA_LOTS_MIN_SIZE,
)
from openprocurement.tender.cfaua.constants import (
    MIN_BIDS_NUMBER as CFA_MIN_BIDS_NUMBER,
)
from openprocurement.tender.competitivedialogue.constants import (
    CD_EU_TYPE,
    CD_UA_TYPE,
    STAGE_2_EU_TYPE,
    STAGE_2_UA_TYPE,
)
from openprocurement.tender.core.constants import (
    AWARD_CRITERIA_LIFE_CYCLE_COST,
    AWARD_CRITERIA_LOWEST_COST,
    AWARD_CRITERIA_RATED_CRITERIA,
    CORE_TENDER_PROCUREMENT_METHOD_TYPES,
)
from openprocurement.tender.core.procedure.models.agreement import (
    AgreementUUID,
    CFASelectionAgreement,
)
from openprocurement.tender.core.procedure.models.criterion import (
    Criterion,
    LimitedCriterion,
    validate_criteria_requirement_uniq,
)
from openprocurement.tender.core.procedure.models.document import PostDocument
from openprocurement.tender.core.procedure.models.feature import (
    CFAFeature,
    CFASelectionFeature,
    Feature,
    validate_related_items,
)
from openprocurement.tender.core.procedure.models.item import (
    CDItem,
    NegotiationItem,
    PQItem,
    ReportingItem,
    TechFeatureItem,
    validate_classification_id,
    validate_related_buyer_in_items,
)
from openprocurement.tender.core.procedure.models.lot import (
    ARMALot,
    ARMAPatchTenderLot,
    ARMAPostTenderLot,
    CFASelectionLot,
    CFASelectionPatchTenderLot,
    CFASelectionPostTenderLot,
    ESCOLot,
    ESCOPatchTenderLot,
    ESCOPostTenderLot,
    LimitedLot,
    LimitedPatchTenderLot,
    LimitedPostTenderLot,
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
    TenderMilestoneType,
    validate_milestones_lot,
)
from openprocurement.tender.core.procedure.models.organization import (
    Organization,
    PQShortlistedFirm,
    ProcuringEntity,
    ReportingFundOrganization,
    ReportingProcuringEntity,
)
from openprocurement.tender.core.procedure.models.period import (
    EnquiryPeriod,
    PeriodStartEndRequired,
    QualificationPeriod,
    StartedPeriodEndRequired,
    TenderAuctionPeriod,
)
from openprocurement.tender.core.procedure.models.tender_base import (
    MAIN_PROCUREMENT_CATEGORY_CHOICES,
    BaseTender,
    CommonBaseTender,
    LimitedCauseDetails,
    PatchBaseTender,
    PostBaseTender,
)
from openprocurement.tender.core.procedure.models.value import (
    BasicValue,
    PostEstimatedValue,
)
from openprocurement.tender.core.procedure.utils import (
    tender_created_after,
)
from openprocurement.tender.core.procedure.validation import (
    validate_funders_ids,
    validate_object_id_uniq,
    validate_pq_criteria_id_uniq,
)
from openprocurement.tender.esco.constants import ESCO
from openprocurement.tender.limited.constants import (
    NEGOTIATION,
    NEGOTIATION_QUICK,
    REPORTING,
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
from openprocurement.tender.pricequotation.constants import PQ


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


class TenderMilestoneMixin(Model):
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_uniq_id])

    def validate_milestones(self, data, value):
        if tender_created_after(MILESTONES_VALIDATION_FROM):
            if value is None or len(value) < 1:
                raise ValidationError("Tender should contain at least one milestone")
        if tender_created_after(REQUIRED_DELIVERY_AND_FINANCING_MILESTONES_VALIDATION_FROM):
            if value is None or not {TenderMilestoneType.DELIVERY, TenderMilestoneType.FINANCING}.issubset(
                set(x.get("type") for x in value)
            ):
                raise ValidationError(
                    f"Tender should contain at least one {TenderMilestoneType.DELIVERY} "
                    f"and one {TenderMilestoneType.FINANCING} milestone"
                )
        validate_milestones_lot(data, value)


class PostTender(TenderMilestoneMixin, PostBaseTender):
    procurementMethodType = StringType(choices=CORE_TENDER_PROCUREMENT_METHOD_TYPES, default=BELOW_THRESHOLD)
    submissionMethod = StringType(
        choices=[
            "electronicAuction",
            # "electronicSubmission",  # never used, submissionMethod unavailable in edit roles
            # "written",
            # "inPerson",
        ],
    )  # Specify the method by which bids must be submitted, in person, written, or electronic auction
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(
        choices=[AWARD_CRITERIA_LOWEST_COST, AWARD_CRITERIA_LIFE_CYCLE_COST],
        default=AWARD_CRITERIA_LOWEST_COST,
    )

    procuringEntity = ModelType(ProcuringEntity, required=True)
    value = ModelType(PostEstimatedValue, required=True)
    guarantee = ModelType(BasicValue)
    minimalStep = ModelType(PostEstimatedValue)
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    auctionPeriod = ModelType(Period)
    items = ListType(
        ModelType(TechFeatureItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    lots = ListType(ModelType(PostTenderLot, required=True), validators=[validate_uniq_id])
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])
    targets = ListType(
        ModelType(PostMetric),
        validators=[validate_uniq_id, validate_observation_ids_uniq],
    )

    def validate_lots(self, data, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_related_items(data, features)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)

    def validate_awardCriteria(self, data, value):
        if value == AWARD_CRITERIA_LIFE_CYCLE_COST and data.get("features"):
            raise ValidationError(f"Can`t add features with {AWARD_CRITERIA_LIFE_CYCLE_COST} awardCriteria")


class PatchTender(PatchBaseTender):
    status = StringType(
        choices=[
            "draft",
            "active.enquiries",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
        ],
    )
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST, AWARD_CRITERIA_LIFE_CYCLE_COST])
    procuringEntity = ModelType(ProcuringEntity)
    value = ModelType(PostEstimatedValue)
    guarantee = ModelType(BasicValue)
    minimalStep = ModelType(PostEstimatedValue)
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired)
    awardPeriod = ModelType(Period)
    items = ListType(
        ModelType(TechFeatureItem, required=True),
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    lots = ListType(ModelType(PatchTenderLot, required=True), validators=[validate_uniq_id])
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_uniq_id])
    targets = ListType(
        ModelType(Metric),
        validators=[validate_uniq_id, validate_observation_ids_uniq],
    )

    def validate_lots(self, data, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")


class Tender(TenderMilestoneMixin, BaseTender):
    procurementMethodType = StringType(choices=CORE_TENDER_PROCUREMENT_METHOD_TYPES, required=True)
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST, AWARD_CRITERIA_LIFE_CYCLE_COST], required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    value = ModelType(PostEstimatedValue, required=True)
    guarantee = ModelType(BasicValue)
    next_check = BaseType()
    minimalStep = ModelType(PostEstimatedValue)
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    auctionPeriod = ModelType(TenderAuctionPeriod)
    items = ListType(
        ModelType(TechFeatureItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    lots = ListType(ModelType(Lot, required=True), validators=[validate_uniq_id])
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])

    qualificationPeriod = ModelType(QualificationPeriod)
    complaintPeriod = BaseType()
    qualifications = BaseType()
    targets = ListType(
        ModelType(Metric),
        validators=[validate_uniq_id, validate_observation_ids_uniq],
    )

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_related_items(data, features)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)

    def validate_awardCriteria(self, data, value):
        if value == AWARD_CRITERIA_LIFE_CYCLE_COST and data.get("features"):
            raise ValidationError(f"Can`t add features with {AWARD_CRITERIA_LIFE_CYCLE_COST} awardCriteria")


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
        ModelType(TechFeatureItem, required=True),
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    documents = ListType(ModelType(PostDocument, required=True))
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    mainProcurementCategory = StringType(choices=MAIN_PROCUREMENT_CATEGORY_CHOICES)
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


class ESCOPostTender(TenderMilestoneMixin, PostBaseTender):
    awardCriteria = StringType(choices=[AWARD_CRITERIA_RATED_CRITERIA], default=AWARD_CRITERIA_RATED_CRITERIA)
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    procurementMethodType = StringType(choices=[ESCO], default=ESCO)
    status = StringType(choices=["draft"], default="draft")
    minValue = ModelType(PostEstimatedValue, default={"currency": "UAH", "valueAddedTaxIncluded": False})
    minimalStepPercentage = DecimalType(min_value=Decimal("0.005"), max_value=Decimal("0.03"), precision=-5)
    yearlyPaymentsPercentageRange = DecimalType(
        min_value=Decimal("0"),
        max_value=Decimal("1"),
        precision=-5,
    )
    NBUdiscountRate = DecimalType(required=True, min_value=Decimal("0"), max_value=Decimal("0.99"), precision=-5)
    fundingKind = StringType(choices=["budget", "other"], required=True, default="other")
    guarantee = ModelType(BasicValue)

    procuringEntity = ModelType(ProcuringEntity, required=True)
    lots = ListType(ModelType(ESCOPostTenderLot, required=True), validators=[validate_uniq_id])
    items = ListType(
        ModelType(TechFeatureItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])
    tenderPeriod = ModelType(StartedPeriodEndRequired, required=True)
    enquiryPeriod = ModelType(EnquiryPeriod)
    auctionPeriod = ModelType(TenderAuctionPeriod)
    awardPeriod = ModelType(Period)

    def validate_yearlyPaymentsPercentageRange(self, data, value):
        validate_esco_yearly_payments_percentage_range(data, value)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_related_items(data, features)

    def validate_lots(self, data, lots):
        validate_esco_lots_yearly_payments_percentage_range(data, lots)

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)


class ESCOPatchTender(PatchBaseTender):
    awardCriteria = StringType(choices=[AWARD_CRITERIA_RATED_CRITERIA])
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    procurementMethodType = StringType(choices=[ESCO])
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
        ],
    )
    minimalStepPercentage = DecimalType(min_value=Decimal("0.005"), max_value=Decimal("0.03"), precision=-5)
    yearlyPaymentsPercentageRange = DecimalType(min_value=Decimal("0"), max_value=Decimal("1"), precision=-5)
    NBUdiscountRate = DecimalType(min_value=Decimal("0"), max_value=Decimal("0.99"), precision=-5)
    fundingKind = StringType(choices=["budget", "other"])
    guarantee = ModelType(BasicValue)

    procuringEntity = ModelType(ProcuringEntity)
    lots = ListType(ModelType(ESCOPatchTenderLot, required=True), validators=[validate_uniq_id])
    items = ListType(ModelType(TechFeatureItem, required=True), min_size=1, validators=[validate_uniq_id])
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_uniq_id])
    tenderPeriod = ModelType(PeriodStartEndRequired)
    enquiryPeriod = ModelType(EnquiryPeriod)


class ESCOTender(TenderMilestoneMixin, BaseTender):
    awardCriteria = StringType(choices=[AWARD_CRITERIA_RATED_CRITERIA], required=True)
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    procurementMethodType = StringType(choices=[ESCO], required=True)
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification.stand-still",
            "active.pre-qualification",
        ],
        required=True,
    )
    minimalStepPercentage = DecimalType(min_value=Decimal("0.005"), max_value=Decimal("0.03"), precision=-5)
    minValue = ModelType(PostEstimatedValue)
    yearlyPaymentsPercentageRange = DecimalType(min_value=Decimal("0"), max_value=Decimal("1"), precision=-5)
    NBUdiscountRate = DecimalType(required=True, min_value=Decimal("0"), max_value=Decimal("0.99"), precision=-5)
    fundingKind = StringType(choices=["budget", "other"], required=True)
    guarantee = ModelType(BasicValue)

    procuringEntity = ModelType(ProcuringEntity, required=True)
    lots = ListType(ModelType(ESCOLot, required=True), validators=[validate_uniq_id])
    items = ListType(
        ModelType(TechFeatureItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    features = ListType(ModelType(Feature, required=True), validators=[validate_uniq_code])
    tenderPeriod = ModelType(PeriodEndRequired, required=True)
    enquiryPeriod = ModelType(EnquiryPeriod)

    auctionPeriod = ModelType(TenderAuctionPeriod)
    awardPeriod = ModelType(Period)

    qualificationPeriod = BaseType()
    qualifications = BaseType()
    complaintPeriod = BaseType()

    next_check = BaseType()

    def validate_yearlyPaymentsPercentageRange(self, data, value):
        validate_esco_yearly_payments_percentage_range(data, value)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_related_items(data, features)

    def validate_lots(self, data, lots):
        validate_esco_lots_yearly_payments_percentage_range(data, lots)

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)


# --- ARMA (complexAsset.arma): no value/minimalStep/features, percentage lots ---


class ARMAPostTender(PostBaseTender):
    procurementMethodType = StringType(choices=[COMPLEX_ASSET_ARMA], default=COMPLEX_ASSET_ARMA)
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_RATED_CRITERIA], default=AWARD_CRITERIA_RATED_CRITERIA)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    guarantee = ModelType(BasicValue)
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    auctionPeriod = ModelType(Period)
    items = ListType(
        ModelType(TechFeatureItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    lots = ListType(ModelType(ARMAPostTenderLot, required=True), validators=[validate_uniq_id])
    milestones = ListType(ModelType(Milestone, required=False), validators=[validate_uniq_id])

    def validate_lots(self, data, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)


class ARMAPatchTender(PatchBaseTender):
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
        ],
    )
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_RATED_CRITERIA], default=AWARD_CRITERIA_RATED_CRITERIA)
    procuringEntity = ModelType(ProcuringEntity)
    guarantee = ModelType(BasicValue)
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired)
    awardPeriod = ModelType(Period)
    items = ListType(
        ModelType(TechFeatureItem, required=True),
        validators=[validate_uniq_id, validate_classification_id],
    )
    lots = ListType(ModelType(ARMAPatchTenderLot, required=True), validators=[validate_uniq_id])
    milestones = ListType(ModelType(Milestone, required=False), validators=[validate_uniq_id])

    def validate_lots(self, data, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")


class ARMATender(BaseTender):
    procurementMethodType = StringType(choices=[COMPLEX_ASSET_ARMA], required=True)
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_RATED_CRITERIA], default=AWARD_CRITERIA_RATED_CRITERIA)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    guarantee = ModelType(BasicValue)
    next_check = BaseType()
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    auctionPeriod = ModelType(TenderAuctionPeriod)
    items = ListType(
        ModelType(TechFeatureItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    lots = ListType(ModelType(ARMALot, required=True), validators=[validate_uniq_id])
    milestones = ListType(ModelType(Milestone, required=False), validators=[validate_uniq_id])

    qualificationPeriod = ModelType(QualificationPeriod)
    complaintPeriod = BaseType()
    qualifications = BaseType()

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)


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


class CFAPostTender(PostTender):
    procurementMethodType = StringType(choices=[CFA_UA], default=CFA_UA)
    mainProcurementCategory = StringType(choices=["goods", "services"])

    agreementDuration = IsoDurationType(required=True, validators=[validate_cfa_max_agreement_duration_period])
    maxAwardsCount = IntType(required=True, validators=[validate_cfa_max_awards_number])

    lots = ListType(
        ModelType(PostTenderLot, required=True),
        required=True,
        min_size=CFA_LOTS_MIN_SIZE,
        max_size=CFA_LOTS_MAX_SIZE,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(CFAFeature, required=True), validators=[validate_uniq_code])
    tenderPeriod = ModelType(StartedPeriodEndRequired, required=True)

    def validate_features(self, data, features):
        validate_cfa_features(data, features)


class CFAPatchTender(PatchTender):
    procurementMethodType = StringType(choices=[CFA_UA])
    mainProcurementCategory = StringType(choices=["goods", "services"])
    agreementDuration = IsoDurationType(validators=[validate_cfa_max_agreement_duration_period])
    maxAwardsCount = IntType(validators=[validate_cfa_max_awards_number])

    lots = ListType(
        ModelType(PatchTenderLot, required=True),
        min_size=CFA_LOTS_MIN_SIZE,
        max_size=CFA_LOTS_MAX_SIZE,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(CFAFeature, required=True), validators=[validate_uniq_code])
    tenderPeriod = ModelType(PeriodStartEndRequired)

    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.qualification",
            "active.qualification.stand-still",
        ],
    )


class CFATender(Tender):
    procurementMethodType = StringType(choices=[CFA_UA], required=True)
    mainProcurementCategory = StringType(choices=["goods", "services"])
    agreementDuration = IsoDurationType(required=True, validators=[validate_cfa_max_agreement_duration_period])
    maxAwardsCount = IntType(required=True, validators=[validate_cfa_max_awards_number])

    lots = ListType(
        ModelType(Lot, required=True),
        required=True,
        min_size=CFA_LOTS_MIN_SIZE,
        max_size=CFA_LOTS_MAX_SIZE,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(CFAFeature, required=True), validators=[validate_uniq_code])
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)

    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
            "active.qualification",
            "active.qualification.stand-still",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
    )

    auctionPeriod = ModelType(Period)
    awards = BaseType()

    def validate_features(self, data, features):
        validate_cfa_features(data, features)


# --- CFA selection (closeFrameworkAgreementSelectionUA) ---


class CFASelectionPostTender(TenderMilestoneMixin, PostBaseTender):
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
        ModelType(TechFeatureItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    lots = ListType(
        ModelType(CFASelectionPostTenderLot, required=True),
        min_size=1,
        max_size=1,
        required=True,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(CFASelectionFeature, required=True), validators=[validate_uniq_code])
    guarantee = ModelType(BasicValue)

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    # Not required milestones
    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_related_items(data, features)


class CFASelectionPatchTender(PatchBaseTender):
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

    items = ListType(
        ModelType(TechFeatureItem, required=True),
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    lots = ListType(
        ModelType(CFASelectionPatchTenderLot, required=True),
        min_size=1,
        max_size=1,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(CFASelectionFeature, required=True), validators=[validate_uniq_code])
    unsuccessfulReason = ListType(StringType, serialize_when_none=False)
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_uniq_id])

    tenderPeriod = ModelType(PeriodEndRequired)
    # will be overwritten by serializable
    minimalStep = ModelType(Value)
    guarantee = ModelType(BasicValue)

    def validate_tenderPeriod(self, data, period):
        if period and get_tender()["status"] != "active.enquiries":
            raise ValidationError("Rogue field")


class CFASelectionTender(TenderMilestoneMixin, BaseTender):
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

    agreements = ListType(ModelType(CFASelectionAgreement, required=True), required=True, min_size=1, max_size=1)
    items = ListType(
        ModelType(TechFeatureItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    lots = ListType(
        ModelType(CFASelectionLot, required=True),
        min_size=1,
        max_size=1,
        required=True,
        validators=[validate_uniq_id],
    )
    features = ListType(ModelType(CFASelectionFeature, required=True), validators=[validate_uniq_code])
    unsuccessfulReason = ListType(StringType, serialize_when_none=False)
    tenderPeriod = ModelType(PeriodEndRequired)
    enquiryPeriod = ModelType(PeriodEndRequired)
    # will be overwritten by serializable
    minimalStep = ModelType(Value)
    value = ModelType(Value)
    guarantee = ModelType(BasicValue)

    next_check = BaseType()

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    # Not required milestones
    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_related_items(data, features)

    @serializable(
        serialized_name="guarantee",
        serialize_when_none=False,
        type=ModelType(BasicValue),
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


# --- priceQuotation ---


def validate_delivery_and_financing_milestones(data, value):
    if tender_created_after(REQUIRED_DELIVERY_AND_FINANCING_MILESTONES_VALIDATION_FROM):
        if value is None or not {TenderMilestoneType.DELIVERY, TenderMilestoneType.FINANCING}.issubset(
            set(x.get("type") for x in value)
        ):
            raise ValidationError(
                f"Tender should contain at least one {TenderMilestoneType.DELIVERY} "
                f"and one {TenderMilestoneType.FINANCING} milestone"
            )
    validate_milestones_lot(data, value)


class PQPostTender(TenderMilestoneMixin, PostBaseTender):
    procurementMethodType = StringType(choices=[PQ], default=PQ)
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST], default=AWARD_CRITERIA_LOWEST_COST)
    status = StringType(choices=["draft"], default="draft")
    agreement = ModelType(AgreementUUID, required=True)
    classification = ModelType(Classification)

    value = ModelType(Value, required=True)
    tenderPeriod = ModelType(StartedPeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    procuringEntity = ModelType(ProcuringEntity, required=True)

    items = ListType(
        ModelType(PQItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )
    criteria = ListType(
        ModelType(Criterion),
        validators=[validate_pq_criteria_id_uniq],
    )

    def validate_milestones(self, data, value):
        validate_delivery_and_financing_milestones(data, value)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)


class PQPatchTender(PatchBaseTender):
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST])
    enquiryPeriod = ModelType(PeriodEndRequired)
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
        ],
    )
    profile = StringType()
    agreement = ModelType(AgreementUUID)

    value = ModelType(Value)
    tenderPeriod = ModelType(PeriodEndRequired)
    awardPeriod = ModelType(Period)
    procuringEntity = ModelType(ProcuringEntity)
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_uniq_id])

    classification = ModelType(Classification)

    items = ListType(
        ModelType(PQItem, required=True),
        min_size=1,
        validators=[validate_uniq_id],
    )
    criteria = ListType(
        ModelType(Criterion),
        validators=[validate_pq_criteria_id_uniq],
    )


class PQTender(TenderMilestoneMixin, BaseTender):
    procurementMethodType = StringType(choices=[PQ], required=True)
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST], required=True)
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
            "active.qualification",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
        required=True,
    )
    profile = StringType()
    agreement = ModelType(AgreementUUID, required=True)
    shortlistedFirms = ListType(ModelType(PQShortlistedFirm))

    value = ModelType(Value, required=True)
    tenderPeriod = ModelType(PeriodStartEndRequired)
    awardPeriod = ModelType(Period)
    procuringEntity = ModelType(ProcuringEntity, required=True)

    classification = ModelType(Classification)
    unsuccessfulReason = ListType(StringType)  # deprecated after PQ bot removing

    items = ListType(
        ModelType(PQItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )
    criteria = ListType(
        ModelType(Criterion),
        validators=[validate_pq_criteria_id_uniq],
    )

    next_check = BaseType()

    def validate_milestones(self, data, value):
        validate_delivery_and_financing_milestones(data, value)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)


# --- limited: reporting ---


def validate_reporting_cause(value):
    if value is not None and value not in TENDER_CAUSE:
        raise ValidationError(f"Value must be one of ['{TENDER_CAUSE}'].")


class ReportingPostTender(TenderMilestoneMixin, PostBaseTender):
    procurementMethodType = StringType(choices=[REPORTING], default=REPORTING)
    procuringEntity = ModelType(ReportingProcuringEntity, required=True)
    items = ListType(
        ModelType(ReportingItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    value = ModelType(Value)
    status = StringType(choices=["draft"], default="draft")

    funders = ListType(
        ModelType(ReportingFundOrganization, required=True),
        validators=[validate_funders_ids],
    )
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDetails = ModelType(LimitedCauseDetails)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)

    def validate_cause(self, data, value):
        validate_reporting_cause(value)


class ReportingPatchTender(CommonBaseTender):
    procurementMethodType = StringType(choices=[REPORTING])
    procuringEntity = ModelType(ReportingProcuringEntity)
    items = ListType(
        ModelType(ReportingItem, required=True),
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    value = ModelType(Value)
    status = StringType(choices=["draft", "active"])
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_uniq_id])

    funders = ListType(
        ModelType(ReportingFundOrganization, required=True),
        validators=[validate_funders_ids],
    )
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDetails = ModelType(LimitedCauseDetails)
    criteria = ListType(
        ModelType(LimitedCriterion, required=True),
        validators=[validate_object_id_uniq, validate_criteria_requirement_uniq],
    )


class ReportingTender(TenderMilestoneMixin, BaseTender):
    procurementMethodType = StringType(choices=[REPORTING], required=True)
    procuringEntity = ModelType(ReportingProcuringEntity, required=True)
    items = ListType(
        ModelType(ReportingItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    value = ModelType(Value)
    status = StringType(choices=["draft", "active", "complete", "cancelled", "unsuccessful"])
    awards = BaseType()
    cancellations = BaseType()

    funders = ListType(
        ModelType(ReportingFundOrganization, required=True),
        validators=[validate_funders_ids],
    )
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDetails = ModelType(LimitedCauseDetails)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)

    def validate_cause(self, data, value):
        validate_reporting_cause(value)


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


class NegotiationPostTender(TenderMilestoneMixin, PostBaseTender):
    procurementMethodType = StringType(choices=[NEGOTIATION], default=NEGOTIATION)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(choices=["draft"], default="draft")
    value = ModelType(Value, required=True)
    items = ListType(
        ModelType(NegotiationItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDescription_ru = StringType()
    causeDetails = ModelType(LimitedCauseDetails)
    lots = ListType(ModelType(LimitedPostTenderLot, required=True), validators=[validate_uniq_id])

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_cause(self, data, value):
        validate_negotiation_cause(value)


class NegotiationPatchTender(CommonBaseTender):
    procurementMethodType = StringType(choices=[NEGOTIATION])
    procuringEntity = ModelType(ProcuringEntity)
    status = StringType(choices=["draft", "active"])
    value = ModelType(Value)
    items = ListType(
        ModelType(NegotiationItem, required=True),
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDescription_ru = StringType()
    causeDetails = ModelType(LimitedCauseDetails)
    lots = ListType(ModelType(LimitedPatchTenderLot, required=True), validators=[validate_uniq_id])

    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_uniq_id])
    criteria = ListType(
        ModelType(LimitedCriterion, required=True),
        validators=[validate_object_id_uniq, validate_criteria_requirement_uniq],
    )


class NegotiationTender(TenderMilestoneMixin, BaseTender):
    procurementMethodType = StringType(choices=[NEGOTIATION], required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(choices=["draft", "active", "complete", "cancelled", "unsuccessful"])
    value = ModelType(Value, required=True)
    items = ListType(
        ModelType(NegotiationItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
    cause = StringType()
    causeDescription = StringType()
    causeDescription_en = StringType()
    causeDescription_ru = StringType()
    causeDetails = ModelType(LimitedCauseDetails)
    lots = ListType(ModelType(LimitedLot, required=True), validators=[validate_uniq_id])

    awards = BaseType()

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_cause(self, data, value):
        validate_negotiation_cause(value)


class NegotiationQuickPostTender(NegotiationPostTender):
    procurementMethodType = StringType(choices=[NEGOTIATION_QUICK], default=NEGOTIATION_QUICK)
    cause = StringType()
    causeDetails = ModelType(LimitedCauseDetails)

    def validate_cause(self, data, value):
        validate_negotiation_quick_cause(value)


class NegotiationQuickPatchTender(NegotiationPatchTender):
    procurementMethodType = StringType(choices=[NEGOTIATION_QUICK])
    causeDetails = ModelType(LimitedCauseDetails)


class NegotiationQuickTender(NegotiationTender):
    procurementMethodType = StringType(choices=[NEGOTIATION_QUICK], required=True)
    cause = StringType()
    causeDetails = ModelType(LimitedCauseDetails)

    def validate_cause(self, data, value):
        validate_negotiation_quick_cause(value)


# --- competitiveDialogue: stage 1 (EU / UA) ---


class CDStage1EUPostTender(PostTender):
    procurementMethodType = StringType(choices=[CD_EU_TYPE], default=CD_EU_TYPE)
    mainProcurementCategory = StringType(choices=["services", "works"])
    items = ListType(
        ModelType(TechFeatureItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)


class CDStage1EUPatchTender(PatchTender):
    procurementMethodType = StringType(choices=[CD_EU_TYPE])
    mainProcurementCategory = StringType(choices=["services", "works"])
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.stage2.waiting",
        ],
    )
    items = ListType(
        ModelType(TechFeatureItem, required=True),
        min_size=1,
        validators=[validate_uniq_id],
    )


class CDStage1EUTender(Tender):
    procurementMethodType = StringType(choices=[CD_EU_TYPE], required=True)
    mainProcurementCategory = StringType(choices=["services", "works"])
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
            "active.qualification",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
            "active.stage2.pending",
            "active.stage2.waiting",
        ],
        required=True,
    )
    items = ListType(
        ModelType(TechFeatureItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )

    stage2TenderID = StringType()  # TODO: move to a distinct endpoint

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)


class CDStage1UAPostTender(CDStage1EUPostTender):
    procurementMethodType = StringType(choices=[CD_UA_TYPE], default=CD_UA_TYPE)


class CDStage1UAPatchTender(CDStage1EUPatchTender):
    procurementMethodType = StringType(choices=[CD_UA_TYPE])


class CDStage1UATender(CDStage1EUTender):
    procurementMethodType = StringType(choices=[CD_UA_TYPE], required=True)


# --- competitiveDialogue: stage 2 (EU / UA) ---


class CDStage2LotId(Model):
    id = StringType()


class CDStage2Firm(Model):
    identifier = ModelType(Identifier, required=True)
    name = StringType(required=True)
    lots = ListType(ModelType(CDStage2LotId, required=True))


def validate_cd_shortlisted_firm_ids(data, firms):
    lot_ids = {e["id"] for e in data.get("lots") or ""}
    for f in firms:
        for lot in f.get("lots") or "":
            lot_id = lot.get("id")
            if lot_id and lot_id not in lot_ids:
                raise ValidationError("id should be one of lots")


class CDStage2EUPostTender(PostTender):
    procurementMethodType = StringType(choices=[STAGE_2_EU_TYPE], default=STAGE_2_EU_TYPE)

    owner = StringType(required=True)
    tenderID = StringType()  # in tests it's not passed
    dialogue_token = StringType(required=True)
    dialogueID = StringType()
    shortlistedFirms = ListType(ModelType(CDStage2Firm, required=True), min_size=3, required=True)

    items = ListType(
        ModelType(CDItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )
    tenderPeriod = ModelType(PeriodEndRequired)

    criteria = ListType(
        ModelType(Criterion, required=True),
        validators=[validate_object_id_uniq, validate_criteria_requirement_uniq],
    )

    @serializable(serialized_name="tenderID")
    def serialize_tender_id(self):
        return self.tenderID  # just return what have been passed

    def validate_awardCriteria(self, data, value):
        return  # to deactivate validation of awardCriteria from parent class

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)

    def validate_shortlistedFirms(self, data, value):
        validate_cd_shortlisted_firm_ids(data, value)


class CDStage2EUPatchTender(PatchTender):
    procurementMethodType = StringType(choices=[STAGE_2_EU_TYPE])

    items = ListType(
        ModelType(CDItem, required=True),
        min_size=1,
        validators=[validate_uniq_id],
    )
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
        ]
    )


class CDStage2EUTender(Tender):
    procurementMethodType = StringType(choices=[STAGE_2_EU_TYPE], required=True)

    dialogue_token = StringType(required=True)
    dialogueID = StringType()

    items = ListType(
        ModelType(CDItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id],
    )
    shortlistedFirms = ListType(ModelType(CDStage2Firm, required=True), min_size=3, required=True)
    status = StringType(
        choices=[
            "draft",
            "draft.stage2",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
            "active.auction",
            "active.qualification",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
    )

    def validate_awardCriteria(self, data, value):
        # for deactivate validation of awardCriteria from parent class
        return

    def validate_shortlistedFirms(self, data, value):
        validate_cd_shortlisted_firm_ids(data, value)

    # Non-required mainProcurementCategory
    def validate_mainProcurementCategory(self, data, value):
        pass

    def validate_milestones(self, data, value):
        validate_delivery_and_financing_milestones(data, value)


class CDStage2UAPostTender(CDStage2EUPostTender):
    procurementMethodType = StringType(choices=[STAGE_2_UA_TYPE], default=STAGE_2_UA_TYPE)


class CDStage2UAPatchTender(CDStage2EUPatchTender):
    procurementMethodType = StringType(choices=[STAGE_2_UA_TYPE])


class CDStage2UATender(CDStage2EUTender):
    procurementMethodType = StringType(choices=[STAGE_2_UA_TYPE], required=True)
