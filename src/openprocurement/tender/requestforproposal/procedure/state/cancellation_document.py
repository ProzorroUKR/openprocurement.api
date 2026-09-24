from openprocurement.tender.core.procedure.state.cancellation_document import (
    CancellationDocumentStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.cancellation import (
    RFPCancellationState,
)


class RFPCancellationDocumentState(CancellationDocumentStateMixin, RFPCancellationState):
    pass
