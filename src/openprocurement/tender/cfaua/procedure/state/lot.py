from openprocurement.tender.cfaua.procedure.state.tender_details import (
    CFAUATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class CFAUATenderLotState(LotStateMixin, CFAUATenderDetailsState):
    pass
