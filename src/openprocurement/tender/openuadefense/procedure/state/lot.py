from openprocurement.tender.openuadefense.procedure.state.tender_details import OpenUATenderDetailsState
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class TenderLotState(LotInvalidationBidStateMixin, OpenUATenderDetailsState):
    pass
