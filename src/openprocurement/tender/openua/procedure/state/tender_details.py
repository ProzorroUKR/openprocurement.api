from openprocurement.tender.core.procedure.state.tender_details import (
    TenderDetailsMixin,
)
from openprocurement.tender.openua.constants import TENDERING_EXTRA_PERIOD
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUATenderDetailsMixin(TenderDetailsMixin):
    pass


class OpenUATenderDetailsState(OpenUATenderDetailsMixin, OpenUATenderState):
    tender_period_extra = TENDERING_EXTRA_PERIOD
    contract_template_required = True
