from schematics.types import BaseType, StringType
from schematics.types.compound import ListType
from schematics.validate import ValidationError

from openprocurement.api.constants import WORKING_DAYS
from openprocurement.api.context import get_now
from openprocurement.api.procedure.models.item import Classification
from openprocurement.api.procedure.models.period import Period, PeriodEndRequired
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import ModelType
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.constants import AWARD_CRITERIA_LOWEST_COST
from openprocurement.tender.core.procedure.models.criterion import Criterion
from openprocurement.tender.core.procedure.models.milestone import (
    Milestone,
    validate_milestones_lot,
)
from openprocurement.tender.core.procedure.models.period import (
    PeriodStartEndRequired,
    StartedPeriodEndRequired,
)
from openprocurement.tender.core.procedure.models.tender import (
    BaseTender,
    PatchBaseTender,
    PostBaseTender,
    validate_related_buyer_in_items,
)
from openprocurement.tender.core.procedure.validation import (
    validate_tender_period_start_date,
)
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.pricequotation.constants import PQ, TENDERING_DURATION
from openprocurement.tender.pricequotation.procedure.models.agreement import Agreement
from openprocurement.tender.pricequotation.procedure.models.item import TenderItem
from openprocurement.tender.pricequotation.procedure.models.organization import (
    ProcuringEntity,
    ShortlistedFirm,
)
from openprocurement.tender.pricequotation.procedure.validation import (
    validate_criteria_id_uniq,
)


def validate_tender_period_duration(data, period):
    tender_period_end_date = calculate_tender_business_date(
        get_now(), TENDERING_DURATION, data, working_days=True, calendar=WORKING_DAYS
    )
    if tender_period_end_date > period.endDate:
        raise ValidationError(f"tenderPeriod must be at least {TENDERING_DURATION.days} full business days long")


class PostTender(PostBaseTender):
    procurementMethodType = StringType(choices=[PQ], default=PQ)
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST], default=AWARD_CRITERIA_LOWEST_COST)
    status = StringType(choices=["draft"], default="draft")
    # profile = StringType()  # Not used anymore
    agreement = ModelType(Agreement, required=True)
    classification = ModelType(Classification)

    value = ModelType(Value, required=True)
    tenderPeriod = ModelType(StartedPeriodEndRequired, required=True)
    awardPeriod = ModelType(Period)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq])

    items = ListType(
        ModelType(TenderItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq],
    )
    criteria = ListType(
        ModelType(Criterion),
        validators=[validate_criteria_id_uniq],
    )

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)

    def validate_tenderPeriod(self, data, period):
        if period.startDate:
            validate_tender_period_start_date(data, period)
        validate_tender_period_duration(data, period)

    def validate_awardPeriod(self, data, period):
        if (
            period
            and period.startDate
            and data.get("tenderPeriod")
            and data.get("tenderPeriod").endDate
            and period.startDate < data.get("tenderPeriod").endDate
        ):
            raise ValidationError("period should begin after tenderPeriod")


class PatchTender(PatchBaseTender):
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
    agreement = ModelType(Agreement)

    value = ModelType(Value)
    tenderPeriod = ModelType(PeriodEndRequired)
    awardPeriod = ModelType(Period)
    procuringEntity = ModelType(ProcuringEntity)
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq])

    classification = ModelType(Classification)

    items = ListType(
        ModelType(TenderItem, required=True),
        min_size=1,
        validators=[validate_items_uniq],
    )
    criteria = ListType(
        ModelType(Criterion),
        validators=[validate_criteria_id_uniq],
    )


class Tender(BaseTender):
    procurementMethodType = StringType(choices=[PQ], required=True)
    submissionMethod = StringType(choices=["electronicAuction"])
    submissionMethodDetails = StringType()  # Any detailed or further information on the submission method.
    submissionMethodDetails_en = StringType()
    submissionMethodDetails_ru = StringType()
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST], required=True)
    status = StringType(
        choices=[
            "draft",
            "draft.publishing",  # deprecated after PQ bot removing
            "draft.unsuccessful",  # deprecated after PQ bot removing
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
    agreement = ModelType(Agreement, required=True)
    shortlistedFirms = ListType(ModelType(ShortlistedFirm))

    value = ModelType(Value, required=True)
    tenderPeriod = ModelType(PeriodStartEndRequired)
    awardPeriod = ModelType(Period)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    milestones = ListType(ModelType(Milestone, required=True), validators=[validate_items_uniq])

    classification = ModelType(Classification)
    unsuccessfulReason = ListType(StringType)  # deprecated after PQ bot removing

    items = ListType(
        ModelType(TenderItem, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq],
    )
    criteria = ListType(
        ModelType(Criterion),
        validators=[validate_criteria_id_uniq],
    )

    contractTemplateName = StringType()
    next_check = BaseType()

    def validate_milestones(self, data, value):
        validate_milestones_lot(data, value)

    def validate_items(self, data, items):
        validate_related_buyer_in_items(data, items)

    def validate_tenderPeriod(self, data, period):
        validate_tender_period_duration(data, period)

    def validate_awardPeriod(self, data, period):
        if (
            period
            and period.startDate
            and data.get("tenderPeriod")
            and data.get("tenderPeriod").endDate
            and period.startDate < data.get("tenderPeriod").endDate
        ):
            raise ValidationError("period should begin after tenderPeriod")
