from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState
from openprocurement.tender.openua.procedure.state.cancellation import OpenUACancellationStateMixing


class OpenEUCancellationStateMixing(OpenUACancellationStateMixing):
    pass


class OpenEUCancellationState(OpenEUCancellationStateMixing, OpenUATenderState):
    pass
