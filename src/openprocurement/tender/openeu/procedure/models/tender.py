from schematics.validate import ValidationError
from schematics.types import IntType, StringType, BaseType
from schematics.types.compound import ModelType, ListType
from openprocurement.tender.core.procedure.models.item import (
    validate_classification_id,
    validate_cpv_group,
)
from openprocurement.tender.openeu.procedure.models.organization import ProcuringEntity
from openprocurement.tender.openeu.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.period import (
    EnquiryPeriod,
    PostPeriodStartEndRequired,
    PeriodStartEndRequired,
)
from openprocurement.tender.core.procedure.models.tender import (
    PostTender as BasePostTender,
    PatchTender as BasePatchTender,
    Tender as BaseTender,
)
from openprocurement.tender.core.constants import AWARD_CRITERIA_LOWEST_COST, AWARD_CRITERIA_LIFE_CYCLE_COST
from openprocurement.tender.openeu.constants import ABOVE_THRESHOLD_EU, TENDERING_DURATION
from openprocurement.tender.openua.validation import _validate_tender_period_start_date
from openprocurement.tender.core.validation import validate_tender_period_duration
from openprocurement.tender.openeu.utils import is_procedure_restricted
from openprocurement.tender.core.utils import validate_features_custom_weight
from openprocurement.tender.core.procedure.models.feature import validate_related_items
from openprocurement.api.validation import validate_items_uniq


class PostTender(BasePostTender):
    procurementMethodType = StringType(choices=[ABOVE_THRESHOLD_EU], default=ABOVE_THRESHOLD_EU)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(choices=["draft"], default="draft")
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

    preQualificationFeaturesRatingBidLimit = IntType()
    preQualificationMinBidsNumber = IntType()
    # targets = ListType(
    #     ModelType(PostMetric),
    #     validators=[validate_metric_ids_uniq, validate_observation_ids_uniq],
    # )

    def validate_awardCriteria(self, data, value):
        if value == AWARD_CRITERIA_LIFE_CYCLE_COST and data.get("features"):
            raise ValidationError(f"Can`t add features with {AWARD_CRITERIA_LIFE_CYCLE_COST} awardCriteria")

    def validate_tenderPeriod(self, data, period):
        if period:
            _validate_tender_period_start_date(data, period)
            validate_tender_period_duration(data, period, TENDERING_DURATION)

    def validate_features(self, data, features):
        validate_related_items(data, features)
        max_features_sum = 0.5 if is_procedure_restricted(data) else 0.3
        validate_features_custom_weight(data, features, max_features_sum)

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
        validators=[validate_cpv_group, validate_items_uniq, validate_classification_id],
    )
    # targets = ListType(
    #     ModelType(Metric),
    #     validators=[validate_metric_ids_uniq, validate_observation_ids_uniq],
    # )


class Tender(BaseTender):
    procurementMethodType = StringType(choices=[ABOVE_THRESHOLD_EU], required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
        ],
    )
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
    # targets = ListType(
    #     ModelType(Metric),
    #     validators=[validate_metric_ids_uniq, validate_observation_ids_uniq],
    # )

    preQualificationFeaturesRatingBidLimit = IntType()
    preQualificationMinBidsNumber = IntType()

    qualificationPeriod = BaseType()
    qualifications = BaseType()
    complaintPeriod = BaseType()

    def validate_awardCriteria(self, data, value):
        if value == AWARD_CRITERIA_LIFE_CYCLE_COST and data.get("features"):
                raise ValidationError(f"Can`t add features with {AWARD_CRITERIA_LIFE_CYCLE_COST} awardCriteria")

    def validate_tenderPeriod(self, data, period):
        validate_tender_period_duration(data, period, TENDERING_DURATION)

    def validate_features(self, data, features):
        validate_related_items(data, features)
        max_features_sum = 0.5 if is_procedure_restricted(data) else 0.3
        validate_features_custom_weight(data, features, max_features_sum)

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
