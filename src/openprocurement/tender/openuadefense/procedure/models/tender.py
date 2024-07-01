from schematics.types import StringType
from schematics.types.compound import ListType, ModelType

from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.procedure.models.item import validate_classification_id
from openprocurement.tender.core.procedure.validation import (
    validate_tender_period_duration,
    validate_tender_period_start_date,
)
from openprocurement.tender.openua.procedure.models.tender import (
    PatchTender as BasePatchTender,
)
from openprocurement.tender.openua.procedure.models.tender import (
    PostTender as BasePostTender,
)
from openprocurement.tender.openua.procedure.models.tender import Tender as BaseTender
from openprocurement.tender.openuadefense.constants import (
    ABOVE_THRESHOLD_UA_DEFENSE,
    TENDERING_DURATION,
)
from openprocurement.tender.openuadefense.procedure.models.item import Item
from openprocurement.tender.openuadefense.procedure.models.organization import (
    ProcuringEntity,
)


class PostTender(BasePostTender):
    procurementMethodType = StringType(choices=[ABOVE_THRESHOLD_UA_DEFENSE], default=ABOVE_THRESHOLD_UA_DEFENSE)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )

    def validate_tenderPeriod(self, data, period):
        if period:
            validate_tender_period_start_date(data, period)
            validate_tender_period_duration(data, period, TENDERING_DURATION, working_days=True)


class PatchTender(BasePatchTender):
    procuringEntity = ModelType(ProcuringEntity)
    items = ListType(
        ModelType(Item, required=True),
        validators=[validate_items_uniq, validate_classification_id],
    )


class Tender(BaseTender):
    procurementMethodType = StringType(choices=[ABOVE_THRESHOLD_UA_DEFENSE], required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)
    items = ListType(
        ModelType(Item, required=True),
        required=True,
        min_size=1,
        validators=[validate_items_uniq, validate_classification_id],
    )

    def validate_tenderPeriod(self, data, period):
        if period:
            validate_tender_period_duration(data, period, TENDERING_DURATION, working_days=True)
