from schematics.types import BaseType, StringType
from schematics.types.compound import ListType, ModelType
from schematics.validate import ValidationError

from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.constants import (
    AWARD_CRITERIA_LIFE_CYCLE_COST,
    AWARD_CRITERIA_LOWEST_COST,
)
from openprocurement.tender.core.procedure.models.feature import validate_related_items
from openprocurement.tender.core.procedure.models.item import validate_classification_id
from openprocurement.tender.core.procedure.models.period import (
    EnquiryPeriod,
    PeriodStartEndRequired,
    PostPeriodStartEndRequired,
)
from openprocurement.tender.core.procedure.models.tender import (
    PatchTender as BasePatchTender,
)
from openprocurement.tender.core.procedure.models.tender import (
    PostTender as BasePostTender,
)
from openprocurement.tender.core.procedure.models.tender import Tender as BaseTender
from openprocurement.tender.core.procedure.utils import validate_features_custom_weight
from openprocurement.tender.core.procedure.validation import (
    validate_tender_period_duration,
    validate_tender_period_start_date,
)
from openprocurement.tender.openeu.constants import (
    ABOVE_THRESHOLD_EU,
    TENDERING_DURATION,
)
from openprocurement.tender.openeu.procedure.models.item import Item
from openprocurement.tender.openeu.procedure.models.organization import ProcuringEntity


class PostTender(BasePostTender):
    procurementMethodType = StringType(choices=[ABOVE_THRESHOLD_EU], default=ABOVE_THRESHOLD_EU)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(choices=["draft"], default="draft")
    awardCriteria = StringType(
        choices=[AWARD_CRITERIA_LOWEST_COST, AWARD_CRITERIA_LIFE_CYCLE_COST], default=AWARD_CRITERIA_LOWEST_COST
    )
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PostPeriodStartEndRequired, required=True)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    # targets = ListType(
    #     ModelType(PostMetric),
    #     validators=[validate_metric_ids_uniq, validate_observation_ids_uniq],
    # )

    def validate_awardCriteria(self, data, value):
        if value == AWARD_CRITERIA_LIFE_CYCLE_COST and data.get("features"):
            raise ValidationError(f"Can`t add features with {AWARD_CRITERIA_LIFE_CYCLE_COST} awardCriteria")

    def validate_tenderPeriod(self, data, period):
        if period:
            validate_tender_period_start_date(data, period)
            validate_tender_period_duration(data, period, TENDERING_DURATION)

    def validate_features(self, data, features):
        validate_related_items(data, features)
        max_features_sum = 0.3
        validate_features_custom_weight(data, features, max_features_sum)


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
        choices=[AWARD_CRITERIA_LOWEST_COST, AWARD_CRITERIA_LIFE_CYCLE_COST],
    )
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodStartEndRequired)
    items = ListType(
        ModelType(Item, required=True),
        validators=[validate_items_uniq, validate_classification_id],
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
            "active.auction",
            "active.qualification",
            "active.awarded",
            "complete",
            "cancelled",
            "unsuccessful",
        ],
    )
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST, AWARD_CRITERIA_LIFE_CYCLE_COST], required=True)
    enquiryPeriod = ModelType(EnquiryPeriod)
    tenderPeriod = ModelType(PeriodStartEndRequired, required=True)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )
    # targets = ListType(
    #     ModelType(Metric),
    #     validators=[validate_metric_ids_uniq, validate_observation_ids_uniq],
    # )

    complaintPeriod = BaseType()

    def validate_awardCriteria(self, data, value):
        if value == AWARD_CRITERIA_LIFE_CYCLE_COST and data.get("features"):
            raise ValidationError(f"Can`t add features with {AWARD_CRITERIA_LIFE_CYCLE_COST} awardCriteria")

    def validate_tenderPeriod(self, data, period):
        validate_tender_period_duration(data, period, TENDERING_DURATION)

    def validate_features(self, data, features):
        validate_related_items(data, features)
        max_features_sum = 0.3
        validate_features_custom_weight(data, features, max_features_sum)
