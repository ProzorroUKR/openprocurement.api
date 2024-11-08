from openprocurement.tender.core.procedure.state.cancellation_document import (
    CancellationDocumentStateMixing,
)
from openprocurement.tender.requestforproposal.procedure.state.cancellation import (
    RequestForProposalCancellationState,
)


class BTCancellationDocumentState(CancellationDocumentStateMixing, RequestForProposalCancellationState):
    pass
