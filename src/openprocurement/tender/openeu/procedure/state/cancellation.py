from openprocurement.tender.openua.procedure.state.cancellation import (
    OpenUACancellationStateMixing,
)
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenEUCancellationStateMixing(OpenUACancellationStateMixing):
    pass


class OpenEUCancellationState(OpenEUCancellationStateMixing, OpenUATenderState):
    pass
