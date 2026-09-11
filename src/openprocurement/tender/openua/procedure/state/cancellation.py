from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixing,
)
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUACancellationStateMixing(CancellationStateMixing):
    cancellation_unsuccessful_items_check = True


class OpenUACancellationState(OpenUACancellationStateMixing, OpenUATenderState):
    pass
