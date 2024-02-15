from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)
from openprocurement.tender.simpledefense.procedure.state.tender import (
    SimpleDefenseTenderState,
)


class SimpleDefenseCancellationComplaintState(CancellationComplaintStateMixin, SimpleDefenseTenderState):
    pass
