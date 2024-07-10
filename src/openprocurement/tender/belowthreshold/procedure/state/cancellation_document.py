from openprocurement.tender.belowthreshold.procedure.state.cancellation import (
    BelowThresholdCancellationState,
)
from openprocurement.tender.core.procedure.state.cancellation_document import (
    CancellationDocumentStateMixing,
)


class BTCancellationDocumentState(CancellationDocumentStateMixing, BelowThresholdCancellationState):
    pass
