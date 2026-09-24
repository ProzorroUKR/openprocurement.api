from openprocurement.tender.core.procedure.state.cancellation_document import (
    CancellationDocumentStateMixin,
)
from openprocurement.tender.open.procedure.state.cancellation import (
    BelowThresholdCancellationState,
    RFPCancellationState,
)


class BelowThresholdCancellationDocumentState(CancellationDocumentStateMixin, BelowThresholdCancellationState):
    pass


class RFPCancellationDocumentState(CancellationDocumentStateMixin, RFPCancellationState):
    pass
