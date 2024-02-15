from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.openeu.procedure.state.cancellation import (
    OpenEUCancellationStateMixing,
)


class CFAUACancellationStateMixing(OpenEUCancellationStateMixing):
    pass


class CFAUACancellationState(CFAUACancellationStateMixing, CFAUATenderState):
    pass
