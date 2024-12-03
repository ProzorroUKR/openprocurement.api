from openprocurement.tender.competitiveordering.procedure.state.tender import (
    OpenTenderState,
)
from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)


class OpenCancellationComplaintState(CancellationComplaintStateMixin, OpenTenderState):
    pass
