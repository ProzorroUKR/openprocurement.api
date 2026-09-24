from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixing


class CFAUACancellationStateMixing(CancellationStateMixing):
    cancellation_unsuccessful_items_check = True
    all_documents_should_be_public = True


class CFAUACancellationState(CFAUACancellationStateMixing, CFAUATenderState):
    pass
