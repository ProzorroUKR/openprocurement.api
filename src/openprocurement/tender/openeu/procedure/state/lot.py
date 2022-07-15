
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState
from openprocurement.tender.openeu.procedure.state.tender_details import TenderDetailsState
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class TenderLotState(LotInvalidationBidStateMixin, OpenEUTenderState):
    tender_details_state_class = TenderDetailsState

