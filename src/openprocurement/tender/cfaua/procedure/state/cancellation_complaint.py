from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)


class CFAUACancellationComplaintState(CancellationComplaintStateMixin, CFAUATenderState):
    pass
