from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixin,
)
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUACancellationStateMixin(CancellationStateMixin):
    cancellation_unsuccessful_items_check = True


class OpenUACancellationState(OpenUACancellationStateMixin, OpenUATenderState):
    pass
