from schematics.exceptions import ValidationError
from schematics.types import BaseType, BooleanType, IntType, StringType
from schematics.types.compound import ModelType

from openprocurement.api.constants import MILESTONES_VALIDATION_FROM
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.period import Period, PeriodEndRequired
from openprocurement.api.procedure.models.value import EstimatedValue
from openprocurement.api.procedure.types import ListType
from openprocurement.api.procedure.validation import validate_features_uniq
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.constants import AWARD_CRITERIA_LOWEST_COST
from openprocurement.tender.core.procedure.models.feature import (
    Feature,
    validate_related_items,
)
from openprocurement.tender.core.procedure.models.guarantee import (
    Guarantee,
    PostGuarantee,
)
from openprocurement.tender.core.procedure.models.item import (
    Item,
    validate_classification_id,
    validate_related_buyer_in_items,
)
from openprocurement.tender.core.procedure.models.lot import (
    Lot,
    PatchTenderLot,
    PostTenderLot,
    validate_lots_uniq,
)
from openprocurement.tender.core.procedure.models.milestone import (
    Milestone,
    validate_milestones_lot,
)
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.period import (
    EnquiryPeriod,
    QualificationPeriod,
    TenderAuctionPeriod,
)
from openprocurement.tender.core.procedure.models.tender_base import (
    BaseTender,
    PatchBaseTender,
    PostBaseTender,
)
from openprocurement.tender.core.procedure.utils import (
    tender_created_after,
    validate_features_custom_weight,
)


def validate_items_related_lot(data, items):
    related_lots = {i["relatedLot"] for i in items if i.get("relatedLot")}

    if related_lots:
        lot_ids = {l["id"] for l in data.get("lots") or []}
        if related_lots - lot_ids:
            raise ValidationError([{'relatedLot': ["relatedLot should be one of lots"]}])


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


class PostTender(PostBaseTender):
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
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST], default=AWARD_CRITERIA_LOWEST_COST)

    procuringEntity = ModelType(ProcuringEntity, required=True)
    value = ModelType(EstimatedValue, required=True)
    guarantee = ModelType(PostGuarantee)
    minimalStep = ModelType(EstimatedValue)
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    auctionPeriod = ModelType(Period)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    lots = ListType(ModelType(PostTenderLot, required=True), validators=[validate_lots_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq])

    def validate_lots(self, data, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_related_items(data, features)
        validate_features_custom_weight(data, features, 0.3)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)

    def validate_milestones(self, data, value):
        if tender_created_after(MILESTONES_VALIDATION_FROM):
            if value is None or len(value) < 1:
                raise ValidationError("Tender should contain at least one milestone")

        validate_milestones_lot(data, value)


class PatchTender(PatchBaseTender):
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST])
    procuringEntity = ModelType(ProcuringEntity)
    value = ModelType(EstimatedValue)
    guarantee = ModelType(Guarantee)
    minimalStep = ModelType(EstimatedValue)
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired)
    awardPeriod = ModelType(Period)
    items = ListType(
        ModelType(Item, required=True), min_size=1, validators=[validate_items_uniq, validate_classification_id]
    )
    lots = ListType(ModelType(PatchTenderLot, required=True), validators=[validate_lots_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq])

    def validate_lots(self, data, value):
        if value and len({lot.guarantee.currency for lot in value if lot.guarantee}) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")


class Tender(BaseTender):
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST], required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    value = ModelType(EstimatedValue, required=True)
    guarantee = ModelType(Guarantee)
    next_check = BaseType()
    minimalStep = ModelType(EstimatedValue)
    enquiryPeriod = ModelType(EnquiryPeriod, required=True)
    tenderPeriod = ModelType(PeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    auctionPeriod = ModelType(TenderAuctionPeriod)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    lots = ListType(ModelType(Lot, required=True), validators=[validate_lots_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq])

    qualificationPeriod = ModelType(QualificationPeriod)
    complaintPeriod = ModelType(Period)
    qualifications = BaseType()
    contractTemplateName = StringType()

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_related_items(data, features)
        validate_features_custom_weight(data, features, 0.3)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)

    def validate_milestones(self, data, value):
        if tender_created_after(MILESTONES_VALIDATION_FROM):
            if value is None or len(value) < 1:
                raise ValidationError("Tender should contain at least one milestone")

        validate_milestones_lot(data, value)


class TenderConfig(Model):
    test = BooleanType()
    hasAuction = BooleanType()
    hasAwardingOrder = BooleanType()
    hasValueRestriction = BooleanType()
    valueCurrencyEquality = BooleanType()
    hasPrequalification = BooleanType()
    minBidsNumber = IntType(min_value=0)
    hasPreSelectionAgreement = BooleanType()
    hasTenderComplaints = BooleanType()
    hasAwardComplaints = BooleanType()
    hasCancellationComplaints = BooleanType()
    hasValueEstimation = BooleanType()
    hasQualificationComplaints = BooleanType()
    tenderComplainRegulation = IntType(min_value=0)
    awardComplainDuration = IntType(min_value=0)
    restricted = BooleanType()

    def validate_valueCurrencyEquality(self, data, value):
        if value is False and any(
            [
                data.get("hasAuction"),
                data.get("hasAwardingOrder"),
                data.get("hasValueRestriction"),
            ]
        ):
            raise ValidationError(
                "valueCurrencyEquality can be False only if "
                "hasAuction=False and "
                "hasAwardingOrder=False and "
                "hasValueRestriction=False"
            )
