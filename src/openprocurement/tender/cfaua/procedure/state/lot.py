from openprocurement.tender.cfaua.procedure.state.tender_details import (
    CFAUATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class TenderLotState(LotInvalidationBidStateMixin, CFAUATenderDetailsState):
    pass
