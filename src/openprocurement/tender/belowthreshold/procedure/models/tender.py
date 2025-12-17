from schematics.types import StringType

from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.api.validation import validate_uniq_id
from openprocurement.tender.belowthreshold.constants import BELOW_THRESHOLD
from openprocurement.tender.core.procedure.models.item import TechFeatureItem as Item
from openprocurement.tender.core.procedure.models.item import validate_classification_id
from openprocurement.tender.core.procedure.models.organization import Organization
from openprocurement.tender.core.procedure.models.period import (
    EnquiryPeriodEndRequired,
    StartedEnquiryPeriodEndRequired,
)
from openprocurement.tender.core.procedure.models.tender import (
    PatchTender as BasePatchTender,
)
from openprocurement.tender.core.procedure.models.tender import (
    PostTender as BasePostTender,
)
from openprocurement.tender.core.procedure.models.tender import Tender as BaseTender


class PostTender(BasePostTender):
    procurementMethodType = StringType(choices=[BELOW_THRESHOLD], default=BELOW_THRESHOLD)
    enquiryPeriod = ModelType(StartedEnquiryPeriodEndRequired, required=True)

    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )


class PatchTender(BasePatchTender):
    enquiryPeriod = ModelType(EnquiryPeriodEndRequired)
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )


class PatchDraftTender(PatchTender):
    inspector = ModelType(Organization)
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )


class Tender(BaseTender):
    procurementMethodType = StringType(choices=[BELOW_THRESHOLD], required=True)
    enquiryPeriod = ModelType(EnquiryPeriodEndRequired, required=True)
    items = ListType(
        ModelType(Item, required=True),
        min_size=1,
        validators=[validate_uniq_id, validate_classification_id],
    )
