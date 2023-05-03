from openprocurement.tender.core.procedure.utils import get_first_revision_date
from openprocurement.tender.core.procedure.models.tender_base import BaseTender, PostBaseTender, PatchBaseTender
from openprocurement.tender.core.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.procedure.models.feature import Feature, validate_related_items
from openprocurement.tender.core.procedure.models.milestone import Milestone, validate_milestones_lot
from openprocurement.tender.core.procedure.models.period import (
    PeriodEndRequired,
    Period,
    TenderAuctionPeriod,
    EnquiryPeriod,
)
from openprocurement.tender.core.procedure.models.guarantee import Guarantee, PostGuarantee
from openprocurement.tender.core.procedure.models.lot import (
    PostTenderLot, PatchTenderLot, Lot,
    validate_lots_uniq, validate_minimal_step_limits
)

from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.api.context import get_now
from openprocurement.tender.core.procedure.models.item import (
    Item,
    validate_related_buyer_in_items,
    validate_classification_id,
    validate_cpv_group,
)
from schematics.exceptions import ValidationError
from schematics.types import (
    BaseType,
    StringType,
    BooleanType,
)
from schematics.types.compound import ModelType
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.models import (
    Value,
    ListType,
    Model,
)
from openprocurement.api.constants import MILESTONES_VALIDATION_FROM
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.validation import validate_milestones
from openprocurement.tender.core.models import validate_features_uniq
from openprocurement.tender.core.utils import (
    validate_features_custom_weight,
)
from openprocurement.tender.core.constants import AWARD_CRITERIA_LOWEST_COST


def validate_minimalstep(data, value):
    if value and value.amount is not None and data.get("value"):
        if data.get("value").amount < value.amount:
            raise ValidationError("value should be less than value of tender")
        if data.get("value").currency != value.currency:
            raise ValidationError("currency should be identical to currency of value of tender")
        if data.get("value").valueAddedTaxIncluded != value.valueAddedTaxIncluded:
            raise ValidationError(
                "valueAddedTaxIncluded should be identical " "to valueAddedTaxIncluded of value of tender"
            )
        if not data.get("lots"):
            validate_minimal_step_limits(data, value)


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
    procurementMethod = StringType(choices=["open", "selective", "limited"], default="open")
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST], default=AWARD_CRITERIA_LOWEST_COST)

    procuringEntity = ModelType(ProcuringEntity, required=True)
    value = ModelType(Value, required=True)
    guarantee = ModelType(PostGuarantee)
    minimalStep = ModelType(Value)
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    auctionPeriod = ModelType(Period)
    items = ListType(ModelType(Item, required=True), required=True, min_size=1,
                     validators=[validate_cpv_group, validate_items_uniq, validate_classification_id])
    lots = ListType(ModelType(PostTenderLot, required=True), validators=[validate_lots_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    milestones = ListType(ModelType(Milestone, required=True),
                          validators=[validate_items_uniq, validate_milestones])

    def validate_lots(self, data, value):
        if value and len(set(lot.guarantee.currency for lot in value if lot.guarantee)) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")

    def validate_minimalStep(self, data, value):
        validate_minimalstep(data, value)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_related_items(data, features)
        validate_features_custom_weight(data, features, 0.3)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)

    def validate_milestones(self, data, value):
        required = get_first_revision_date(get_tender(), default=get_now()) > MILESTONES_VALIDATION_FROM
        if required and (value is None or len(value) < 1):
            raise ValidationError("Tender should contain at least one milestone")

        validate_milestones_lot(data, value)


class PatchTender(PatchBaseTender):
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    procurementMethod = StringType(choices=["open"])
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST])
    procuringEntity = ModelType(ProcuringEntity)
    value = ModelType(Value)
    guarantee = ModelType(Guarantee)
    minimalStep = ModelType(Value)
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodEndRequired)
    awardPeriod = ModelType(Period)
    items = ListType(ModelType(Item, required=True), min_size=1,
                     validators=[validate_cpv_group, validate_items_uniq, validate_classification_id])
    lots = ListType(ModelType(PatchTenderLot, required=True), validators=[validate_lots_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    milestones = ListType(ModelType(Milestone, required=True),
                          validators=[validate_items_uniq, validate_milestones])

    def validate_lots(self, data, value):
        if value and len(set(lot.guarantee.currency for lot in value if lot.guarantee)) > 1:
            raise ValidationError("lot guarantee currency should be identical to tender guarantee currency")


class Tender(BaseTender):
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    procurementMethod = StringType(choices=["open"], required=True)
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST], required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    value = ModelType(Value, required=True)
    guarantee = ModelType(Guarantee)
    next_check = BaseType()
    minimalStep = ModelType(Value)
    enquiryPeriod = ModelType(EnquiryPeriod, required=True)
    tenderPeriod = ModelType(PeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    auctionPeriod = ModelType(TenderAuctionPeriod)
    items = ListType(ModelType(Item, required=True), required=True, min_size=1,
                     validators=[validate_cpv_group, validate_items_uniq, validate_classification_id])
    lots = ListType(ModelType(Lot, required=True), validators=[validate_lots_uniq])
    features = ListType(ModelType(Feature, required=True), validators=[validate_features_uniq])
    milestones = ListType(ModelType(Milestone, required=True),
                          validators=[validate_items_uniq, validate_milestones])

    def validate_minimalStep(self, data, value):
        validate_minimalstep(data, value)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)
        validate_items_related_lot(data, items)

    def validate_features(self, data, features):
        validate_related_items(data, features)
        validate_features_custom_weight(data, features, 0.3)

    def validate_awardPeriod(self, data, period):
        validate_award_period(data, period)

    def validate_milestones(self, data, value):
        required = get_first_revision_date(get_tender(), default=get_now()) > MILESTONES_VALIDATION_FROM
        if required and (value is None or len(value) < 1):
            raise ValidationError("Tender should contain at least one milestone")

        validate_milestones_lot(data, value)


class TenderConfig(Model):
    test = BooleanType(required=False)
    hasAuction = BooleanType(required=False)
