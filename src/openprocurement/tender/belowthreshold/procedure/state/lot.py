from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState


class TenderLotState(BelowThresholdTenderState, LotStateMixin):
    pass
