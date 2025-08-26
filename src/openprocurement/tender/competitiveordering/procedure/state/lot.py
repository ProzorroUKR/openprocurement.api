from openprocurement.tender.competitiveordering.procedure.state.tender_details import (
    COLongTenderDetailsState,
    COShortTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class COShortTenderLotState(LotInvalidationBidStateMixin, COShortTenderDetailsState):
    pass


class COLongTenderLotState(LotInvalidationBidStateMixin, COLongTenderDetailsState):
    pass
