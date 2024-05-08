from schematics.types import StringType
from schematics.types.compound import ListType, ModelType
from schematics.validate import ValidationError

from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.constants import (
    AWARD_CRITERIA_LIFE_CYCLE_COST,
    AWARD_CRITERIA_LOWEST_COST,
)
from openprocurement.tender.core.procedure.models.item import validate_classification_id
from openprocurement.tender.core.procedure.models.metric import (
    Metric,
    PostMetric,
    validate_metric_ids_uniq,
    validate_observation_ids_uniq,
)
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
from openprocurement.tender.core.procedure.validation import (
    validate_tender_period_duration,
    validate_tender_period_start_date,
)
from openprocurement.tender.openua.constants import (
    ABOVE_THRESHOLD_UA,
    TENDERING_DURATION,
)
from openprocurement.tender.openua.procedure.models.item import Item
from openprocurement.tender.openua.procedure.models.organization import ProcuringEntity


class PostTender(BasePostTender):
    procuringEntity = ModelType(ProcuringEntity, required=True)
    status = StringType(choices=["draft"], default="draft")
    procurementMethodType = StringType(choices=[ABOVE_THRESHOLD_UA], default=ABOVE_THRESHOLD_UA)
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
    targets = ListType(
        ModelType(PostMetric),
        validators=[validate_metric_ids_uniq, validate_observation_ids_uniq],
    )

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
        choices=[AWARD_CRITERIA_LOWEST_COST, AWARD_CRITERIA_LIFE_CYCLE_COST],
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
    awardCriteria = StringType(choices=[AWARD_CRITERIA_LOWEST_COST, AWARD_CRITERIA_LIFE_CYCLE_COST], required=True)
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

    def validate_awardCriteria(self, data, value):
        if value == AWARD_CRITERIA_LIFE_CYCLE_COST:
            if data.get("features", []):
                raise ValidationError("Can`t add features with {} awardCriteria".format(AWARD_CRITERIA_LIFE_CYCLE_COST))

    def validate_tenderPeriod(self, data, period):
        if period:
            validate_tender_period_duration(data, period, TENDERING_DURATION)
