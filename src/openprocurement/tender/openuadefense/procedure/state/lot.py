from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin
from openprocurement.tender.openuadefense.procedure.state.tender_details import (
    OpenUATenderDetailsState,
)


class TenderLotState(LotInvalidationBidStateMixin, OpenUATenderDetailsState):
    pass
