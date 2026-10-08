from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)


class ARMACancellationComplaintState(CancellationComplaintStateMixin, ARMATenderState):
    pass
