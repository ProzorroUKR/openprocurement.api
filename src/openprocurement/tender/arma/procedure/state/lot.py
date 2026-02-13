from openprocurement.tender.arma.procedure.state.tender_details import (
    TenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class LotState(LotInvalidationBidStateMixin, TenderDetailsState):
    pass
