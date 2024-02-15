from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)
from openprocurement.tender.openuadefense.procedure.state.tender import (
    OpenUADefenseTenderState,
)


class OpenUADefenseCancellationComplaintState(CancellationComplaintStateMixin, OpenUADefenseTenderState):
    pass
