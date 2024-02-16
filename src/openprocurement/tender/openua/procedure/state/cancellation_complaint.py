from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUACancellationComplaintState(CancellationComplaintStateMixin, OpenUATenderState):
    pass
