from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.openua.procedure.state.tender_details import (
    OpenUATenderDetailsState,
)


class OpenUATenderLotState(LotStateMixin, OpenUATenderDetailsState):
    pass
