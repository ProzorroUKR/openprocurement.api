from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState


class TenderLotState(LotStateMixin, CFASelectionTenderState):
    pass
