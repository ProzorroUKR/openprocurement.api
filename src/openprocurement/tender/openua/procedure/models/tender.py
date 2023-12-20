from schematics.validate import ValidationError
from schematics.types import StringType, BaseType
from schematics.types.serializable import serializable
from schematics.types.compound import ModelType, ListType
from openprocurement.tender.core.procedure.models.item import (
    validate_classification_id,
)
from openprocurement.api.procedure.models.item import validate_cpv_group
from openprocurement.tender.openua.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.metric import (
    PostMetric, Metric,
    validate_metric_ids_uniq,
    validate_observation_ids_uniq,
)
from openprocurement.tender.core.procedure.models.period import (
    EnquiryPeriod,
    PostPeriodStartEndRequired,
    PeriodStartEndRequired,
)
from openprocurement.api.procedure.models.period import Period
from openprocurement.tender.core.procedure.models.tender import (
    PostTender as BasePostTender,
    PatchTender as BasePatchTender,
    Tender as BaseTender,
)
from openprocurement.tender.openua.procedure.models.organization import ProcuringEntity
from openprocurement.tender.core.constants import AWARD_CRITERIA_LOWEST_COST, AWARD_CRITERIA_LIFE_CYCLE_COST
from openprocurement.tender.core.utils import (
    calculate_complaint_business_date,
)
from openprocurement.tender.openua.constants import (
    ABOVE_THRESHOLD_UA,
    COMPLAINT_SUBMIT_TIME,
    TENDERING_DURATION,
)
from openprocurement.tender.core.procedure.validation import (
    validate_tender_period_start_date,
    validate_tender_period_duration,
)
from openprocurement.api.validation import validate_items_uniq


class PostTender(BasePostTender):
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(choices=["draft"], default="draft")
    procurementMethodType = StringType(choices=[ABOVE_THRESHOLD_UA], default=ABOVE_THRESHOLD_UA)
    awardCriteria = StringType(
        choices=[
            AWARD_CRITERIA_LOWEST_COST,
            AWARD_CRITERIA_LIFE_CYCLE_COST
        ],
        default=AWARD_CRITERIA_LOWEST_COST
    )
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PostPeriodStartEndRequired, required=True)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    targets = ListType(
        ModelType(PostMetric),
        validators=[validate_metric_ids_uniq, validate_observation_ids_uniq],
    )

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        end_date = calculate_complaint_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME, self)
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=end_date))

    def validate_awardCriteria(self, data, value):
        if value == AWARD_CRITERIA_LIFE_CYCLE_COST:
            if data.get("features", []):
                raise ValidationError("Can`t add features with {} awardCriteria".format(AWARD_CRITERIA_LIFE_CYCLE_COST))

    def validate_tenderPeriod(self, data, period):
        if period:
            validate_tender_period_start_date(data, period)
            validate_tender_period_duration(data, period, TENDERING_DURATION)


class PatchTender(BasePatchTender):
    procuringEntity = ModelType(ProcuringEntity)
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification.stand-still",
        ],
    )
    awardCriteria = StringType(
        choices=[
            AWARD_CRITERIA_LOWEST_COST,
            AWARD_CRITERIA_LIFE_CYCLE_COST
        ],
    )
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodStartEndRequired)
    items = ListType(
        ModelType(Item, required=True),
        validators=[validate_items_uniq, validate_classification_id],
    )
    targets = ListType(
        ModelType(Metric),
        validators=[validate_metric_ids_uniq, validate_observation_ids_uniq],
    )


class Tender(BaseTender):
    procuringEntity = ModelType(ProcuringEntity, required=True)
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
    )
    procurementMethodType = StringType(choices=[ABOVE_THRESHOLD_UA], required=True)
    awardCriteria = StringType(
        choices=[
            AWARD_CRITERIA_LOWEST_COST,
            AWARD_CRITERIA_LIFE_CYCLE_COST
        ],
        required=True
    )
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    targets = ListType(
        ModelType(Metric),
        validators=[validate_metric_ids_uniq, validate_observation_ids_uniq],
    )

    @serializable(type=ModelType(Period))
    def complaintPeriod(self):
        end_date = calculate_complaint_business_date(self.tenderPeriod.endDate, -COMPLAINT_SUBMIT_TIME, self)
        return Period(dict(startDate=self.tenderPeriod.startDate, endDate=end_date))

    def validate_awardCriteria(self, data, value):
        if value == AWARD_CRITERIA_LIFE_CYCLE_COST:
            if data.get("features", []):
                raise ValidationError("Can`t add features with {} awardCriteria".format(AWARD_CRITERIA_LIFE_CYCLE_COST))

    def validate_tenderPeriod(self, data, period):
        if period:
            validate_tender_period_duration(data, period, TENDERING_DURATION)
