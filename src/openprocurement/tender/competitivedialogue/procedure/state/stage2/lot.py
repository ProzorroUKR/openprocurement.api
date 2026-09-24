from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDEUStage2TenderDetailsState,
    CDUAStage2TenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class CDStage2EUTenderLotState(LotInvalidationBidStateMixin, CDEUStage2TenderDetailsState):
    lot_operations_forbidden = True


class CDStage2UATenderLotState(LotInvalidationBidStateMixin, CDUAStage2TenderDetailsState):
    lot_operations_forbidden = True
