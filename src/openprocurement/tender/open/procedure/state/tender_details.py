from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixin,
)
from openprocurement.tender.open.constants import (
    TENDERING_EXTRA_PERIOD,
    WORKING_DAYS_CONFIG,
)
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenTenderDetailsState(TenderDetailsMixin, OpenTenderState):
    tender_period_extra = TENDERING_EXTRA_PERIOD
    contract_template_required = True
    working_days_config = WORKING_DAYS_CONFIG
