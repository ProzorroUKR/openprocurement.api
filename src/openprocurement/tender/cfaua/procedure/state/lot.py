from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.cfaua.procedure.state.tender_details import TenderDetailsState


class TenderLotState(LotInvalidationBidStateMixin, CFAUATenderState):
    tender_details_state_class = TenderDetailsState

