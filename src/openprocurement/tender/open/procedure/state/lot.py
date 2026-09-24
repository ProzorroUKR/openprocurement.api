from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.open.procedure.state.tender_details import (
    OpenTenderDetailsState,
)


class OpenTenderLotState(LotStateMixin, OpenTenderDetailsState):
    pass
