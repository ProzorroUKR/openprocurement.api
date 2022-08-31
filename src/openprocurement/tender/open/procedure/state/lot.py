from openprocurement.tender.open.procedure.state.tender import OpenTenderState
from openprocurement.tender.open.procedure.state.tender_details import TenderDetailsState
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class TenderLotState(LotInvalidationBidStateMixin, OpenTenderState):
    tender_details_state_class = TenderDetailsState

