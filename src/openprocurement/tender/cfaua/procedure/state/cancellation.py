from openprocurement.tender.openeu.procedure.state.cancellation import OpenEUCancellationStateMixing
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState


class CFAUACancellationStateMixing(OpenEUCancellationStateMixing):
    pass


class CFAUACancellationState(CFAUACancellationStateMixing, CFAUATenderState):
    pass
