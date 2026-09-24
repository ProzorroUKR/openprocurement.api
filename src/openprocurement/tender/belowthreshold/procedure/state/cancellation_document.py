from openprocurement.tender.belowthreshold.procedure.state.cancellation import (
    BelowThresholdCancellationState,
)
from openprocurement.tender.core.procedure.state.cancellation_document import (
    CancellationDocumentStateMixin,
)


class BelowThresholdCancellationDocumentState(CancellationDocumentStateMixin, BelowThresholdCancellationState):
    pass
