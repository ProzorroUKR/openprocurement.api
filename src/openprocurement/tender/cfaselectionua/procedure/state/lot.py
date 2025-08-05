from openprocurement.tender.cfaselectionua.procedure.state.tender_details import (
    CFASelectionTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class TenderLotState(LotStateMixin, CFASelectionTenderDetailsState):
    should_validate_lot_minimal_step = False
