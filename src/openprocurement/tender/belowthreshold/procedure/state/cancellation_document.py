from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.belowthreshold.procedure.state.cancellation import (
    BelowThresholdCancellationState,
)
from openprocurement.tender.core.procedure.context import get_cancellation, get_request
from openprocurement.tender.core.procedure.state.cancellation_document import (
    CancellationDocumentStateMixing,
)


class BTCancellationDocumentState(CancellationDocumentStateMixing, BelowThresholdCancellationState):
    pass
