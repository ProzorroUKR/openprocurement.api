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
