from openprocurement.tender.competitiveordering.procedure.state.tender_details import (
    COLongTenderDetailsState,
    COShortTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class COShortTenderLotState(LotStateMixin, COShortTenderDetailsState):
    invalidate_bids_on_lot_change = True


class COLongTenderLotState(LotStateMixin, COLongTenderDetailsState):
    invalidate_bids_on_lot_change = True
