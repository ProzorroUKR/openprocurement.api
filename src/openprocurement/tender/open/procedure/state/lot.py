from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin
from openprocurement.tender.open.procedure.state.tender_details import (
    OpenTenderDetailsState,
)


class TenderLotState(LotInvalidationBidStateMixin, OpenTenderDetailsState):
    pass
