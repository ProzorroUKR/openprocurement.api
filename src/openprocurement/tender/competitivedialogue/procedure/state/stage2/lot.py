from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDEUStage2TenderDetailsState,
    CDUAStage2TenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class CDStage2EUTenderLotState(LotStateMixin, CDEUStage2TenderDetailsState):
    invalidate_bids_on_lot_change = True
    lot_operations_forbidden = True


class CDStage2UATenderLotState(LotStateMixin, CDUAStage2TenderDetailsState):
    invalidate_bids_on_lot_change = True
    lot_operations_forbidden = True
