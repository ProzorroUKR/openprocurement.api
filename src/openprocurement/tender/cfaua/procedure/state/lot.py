from openprocurement.tender.cfaua.constants import LOTS_MAX_SIZE, LOTS_MIN_SIZE
from openprocurement.tender.cfaua.procedure.state.tender_details import (
    CFAUATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotInvalidationBidStateMixin


class TenderLotState(LotInvalidationBidStateMixin, CFAUATenderDetailsState):
    lots_min_count = LOTS_MIN_SIZE
    lots_max_count = LOTS_MAX_SIZE
