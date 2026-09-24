from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.limited.procedure.models.lot import LimitedLot, LimitedPatchLot, LimitedPostLot
from openprocurement.tender.limited.procedure.state.tender_details import (
    NegotiationTenderDetailsState,
)


class NegotiationLotState(LotStateMixin, NegotiationTenderDetailsState):
    post_data_model = LimitedPostLot
    patch_data_model = LimitedPatchLot
    data_model = LimitedLot
    lot_operation_allowed_tender_statuses = ("draft", "active")
    lot_updates_tender_values = False
    lot_operations_forbidden_with_awards = True
