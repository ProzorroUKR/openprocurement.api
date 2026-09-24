from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.requestforproposal.procedure.state.tender_details import (
    RFPTenderDetailsState,
)


class RFPTenderLotState(LotStateMixin, RFPTenderDetailsState):
    lot_operation_allowed_tender_statuses = ("active.enquiries", "active.tendering", "draft")
    invalidate_bids_on_lot_change = False

    pass
