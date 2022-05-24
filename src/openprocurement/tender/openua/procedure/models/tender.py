from schematics.validate import ValidationError
from schematics.types import StringType
from schematics.types.serializable import serializable
from schematics.types.compound import ModelType, ListType
from openprocurement.tender.core.procedure.models.item import (
    validate_classification_id,
    validate_cpv_group,
)
from openprocurement.tender.openua.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.metric import (
    PostMetric, Metric,
    validate_metric_ids_uniq, validate_observation_ids_uniq,
)
from openprocurement.tender.core.procedure.models.period import (
    EnquiryPeriod,
    PostPeriodStartEndRequired,
    PeriodStartEndRequired,
    Period,
)
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
from openprocurement.tender.openua.validation import _validate_tender_period_start_date
from openprocurement.tender.core.validation import validate_tender_period_duration
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
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
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
            _validate_tender_period_start_date(data, period)
            validate_tender_period_duration(data, period, TENDERING_DURATION)

    # @serializable(
    #     serialized_name="enquiryPeriod",
    #     serialize_when_none=True,
    #     type=ModelType(EnquiryPeriod, required=False)
    # )
    # def tender_enquiryPeriod(self):
    #     enquiry_period_class = self._fields["enquiryPeriod"]
    #     end_date = calculate_tender_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, self)
    #     clarifications_until = calculate_clarif_business_date(end_date, ENQUIRY_STAND_STILL_TIME, self, True)
    #     return enquiry_period_class(
    #         dict(
    #             startDate=self.tenderPeriod.startDate,
    #             endDate=end_date,
    #             invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
    #             clarificationsUntil=clarifications_until,
    #         )
    #     )


class PatchTender(BasePatchTender):
    procuringEntity = ModelType(ProcuringEntity)
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
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
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
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
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
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

    # @serializable(
    #     serialized_name="enquiryPeriod",
    #     serialize_when_none=True,
    #     type=ModelType(EnquiryPeriod, required=False)
    # )
    # def tender_enquiryPeriod(self):
    #     enquiry_period_class = self._fields["enquiryPeriod"]
    #     end_date = calculate_tender_business_date(self.tenderPeriod.endDate, -ENQUIRY_PERIOD_TIME, self)
    #     clarifications_until = calculate_clarif_business_date(end_date, ENQUIRY_STAND_STILL_TIME, self, True)
    #     return enquiry_period_class(
    #         dict(
    #             startDate=self.tenderPeriod.startDate,
    #             endDate=end_date,
    #             invalidationDate=self.enquiryPeriod and self.enquiryPeriod.invalidationDate,
    #             clarificationsUntil=clarifications_until,
    #         )
    #     )
