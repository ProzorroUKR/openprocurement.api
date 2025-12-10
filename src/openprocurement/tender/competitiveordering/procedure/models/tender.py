from schematics.types import StringType
from schematics.types.compound import ListType, ModelType

from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.models.item import Item
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


class PostTender(BasePostTender):
    status = StringType(choices=["draft"], default="draft")
    procurementMethodType = StringType(choices=[COMPETITIVE_ORDERING], default=COMPETITIVE_ORDERING)
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


class PatchTender(BasePatchTender):
    status = StringType(
        choices=[
            "draft",
            "active.tendering",
            "active.pre-qualification",
            "active.pre-qualification.stand-still",
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
    procurementMethodType = StringType(choices=[COMPETITIVE_ORDERING], required=True)
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
