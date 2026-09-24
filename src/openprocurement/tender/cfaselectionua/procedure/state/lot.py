from openprocurement.tender.cfaselectionua.procedure.models.lot import (
    CFASelectionLot,
    CFASelectionPatchLot,
    CFASelectionPostLot,
)
from openprocurement.tender.cfaselectionua.procedure.state.tender_details import (
    CFASelectionTenderDetailsState,
)
from openprocurement.tender.core.procedure.state.lot import LotStateMixin


class CFASelectionTenderLotState(LotStateMixin, CFASelectionTenderDetailsState):
    post_data_model = CFASelectionPostLot
    patch_data_model = CFASelectionPatchLot
    data_model = CFASelectionLot

    lot_operation_allowed_tender_statuses = ("active.enquiries", "draft")
    lot_minimal_step_check = False
    invalidate_bids_on_lot_change = False
