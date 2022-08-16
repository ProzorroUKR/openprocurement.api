from openprocurement.tender.core.procedure.context import get_request, get_tender, get_cancellation
from openprocurement.tender.core.procedure.state.cancellation_document import CancellationDocumentStateMixing
from openprocurement.tender.belowthreshold.procedure.state.cancellation import BelowThresholdCancellationState


class BTCancellationDocumentState(CancellationDocumentStateMixing, BelowThresholdCancellationState):
    pass

