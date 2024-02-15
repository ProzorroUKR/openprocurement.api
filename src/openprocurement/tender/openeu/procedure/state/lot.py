from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin
from openprocurement.tender.openeu.procedure.state.tender_details import (
    OpenEUTenderDetailsState,
)


class TenderLotState(LotInvalidationBidStateMixin, OpenEUTenderDetailsState):
    pass
