from openprocurement.tender.core.procedure.state.lot import LotStateMixin
from openprocurement.tender.limited.procedure.state.tender_details import (
    NegotiationTenderDetailsState,
)


class NegotiationLotState(LotStateMixin, NegotiationTenderDetailsState):
    lot_updates_tender_values = False
    lot_operations_forbidden_with_awards = True
