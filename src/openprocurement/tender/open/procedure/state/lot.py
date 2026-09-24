from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.open.procedure.state.tender_details import (
    OpenTenderDetailsState,
)


class TenderLotState(LotStateMixin, OpenTenderDetailsState):
    invalidate_bids_on_lot_change = True
