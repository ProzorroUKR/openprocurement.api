from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.openua.procedure.state.tender_details import (
    OpenUATenderDetailsState,
)


class TenderLotState(LotStateMixin, OpenUATenderDetailsState):
    invalidate_bids_on_lot_change = True
