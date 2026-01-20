from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.openeu.procedure.state.cancellation import (
    OpenEUCancellationStateMixing,
)


class CFAUACancellationStateMixing(OpenEUCancellationStateMixing):
    all_documents_should_be_public = True


class CFAUACancellationState(CFAUACancellationStateMixing, CFAUATenderState):
    pass
