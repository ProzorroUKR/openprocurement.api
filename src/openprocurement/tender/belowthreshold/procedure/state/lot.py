from openprocurement.tender.belowthreshold.procedure.state.tender_details import (
    BelowThresholdTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class TenderLotState(LotStateMixin, BelowThresholdTenderDetailsState):
    pass
