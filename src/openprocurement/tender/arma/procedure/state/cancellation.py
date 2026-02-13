from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.openua.procedure.state.cancellation import (
    OpenUACancellationStateMixing,
)


class CancellationState(OpenUACancellationStateMixing, TenderState):
    pass
