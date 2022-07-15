from openprocurement.tender.openuadefense.procedure.state.tender import OpenUADefenseTenderState
from openprocurement.tender.openuadefense.procedure.state.tender_details import TenderDetailsState
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class TenderLotState(LotInvalidationBidStateMixin, OpenUADefenseTenderState):
    tender_details_state_class = TenderDetailsState
