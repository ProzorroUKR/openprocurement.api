from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.openeu.procedure.state.tender_details import (
    OpenEUTenderDetailsState,
)


class OpenEUTenderLotState(LotStateMixin, OpenEUTenderDetailsState):
    pass
