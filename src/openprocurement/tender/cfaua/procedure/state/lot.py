from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin
from openprocurement.tender.cfaua.procedure.state.tender_details import CFAUATenderDetailsState


class TenderLotState(LotInvalidationBidStateMixin, CFAUATenderDetailsState):
    pass
