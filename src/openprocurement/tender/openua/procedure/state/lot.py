from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState
from openprocurement.tender.openua.procedure.state.tender_details import TenderDetailsState
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class TenderLotState(LotInvalidationBidStateMixin, OpenUATenderState):
    tender_details_state_class = TenderDetailsState

