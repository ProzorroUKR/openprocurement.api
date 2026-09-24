from openprocurement.tender.belowthreshold.procedure.state.tender_details import (
    BelowThresholdTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class BelowThresholdTenderLotState(LotStateMixin, BelowThresholdTenderDetailsState):
    lot_operation_allowed_tender_statuses = ("active.enquiries", "draft")
    invalidate_bids_on_lot_change = False

    pass
