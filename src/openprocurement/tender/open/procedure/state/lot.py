from openprocurement.tender.open.procedure.state.tender_details import OpenTenderDetailsState
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class TenderLotState(LotInvalidationBidStateMixin, OpenTenderDetailsState):
    pass
