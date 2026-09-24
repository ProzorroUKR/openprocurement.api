from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixin


class ARMACancellationState(CancellationStateMixin, ARMATenderState):
    cancellation_unsuccessful_items_check = True
