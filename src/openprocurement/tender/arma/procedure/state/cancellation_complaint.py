from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)


class CancellationComplaintState(CancellationComplaintStateMixin, TenderState):
    pass
