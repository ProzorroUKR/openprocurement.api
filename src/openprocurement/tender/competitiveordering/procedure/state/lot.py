from openprocurement.tender.competitiveordering.procedure.state.tender_details import (
    COTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class CompetitiveOrderingTenderLotState(LotInvalidationBidStateMixin, COTenderDetailsState):
    pass
