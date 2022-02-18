from schematics.types import StringType
from schematics.types.compound import ModelType
from openprocurement.tender.openuadefense.procedure.models.organization import ProcuringEntity
from openprocurement.tender.openua.procedure.models.tender import (
    PostTender as BasePostTender,
    PatchTender as BasePatchTender,
    Tender as BaseTender,
)
from openprocurement.tender.openuadefense.constants import (
    ABOVE_THRESHOLD_UA_DEFENSE,
    TENDERING_DURATION,
)
from openprocurement.tender.openua.validation import _validate_tender_period_start_date
from openprocurement.tender.core.validation import validate_tender_period_duration


class PostTender(BasePostTender):
    procurementMethodType = StringType(choices=[ABOVE_THRESHOLD_UA_DEFENSE], default=ABOVE_THRESHOLD_UA_DEFENSE)
    procuringEntity = ModelType(ProcuringEntity, required=True)

    def validate_tenderPeriod(self, data, period):
        if period:
            _validate_tender_period_start_date(data, period)
            validate_tender_period_duration(data, period, TENDERING_DURATION, working_days=True)


class PatchTender(BasePatchTender):
    procuringEntity = ModelType(ProcuringEntity)


class Tender(BaseTender):
    procurementMethodType = StringType(choices=[ABOVE_THRESHOLD_UA_DEFENSE], required=True)
    procuringEntity = ModelType(ProcuringEntity, required=True)

    def validate_tenderPeriod(self, data, period):
        if period:
            validate_tender_period_duration(data, period, TENDERING_DURATION, working_days=True)
