from openprocurement.tender.cfaua.constants import CFA_UA_LOTS_MAX_SIZE, CFA_UA_LOTS_MIN_SIZE
from openprocurement.tender.cfaua.procedure.state.tender_details import (
    CFAUATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class CFAUATenderLotState(LotStateMixin, CFAUATenderDetailsState):
    lots_min_count = CFA_UA_LOTS_MIN_SIZE
    lots_max_count = CFA_UA_LOTS_MAX_SIZE
