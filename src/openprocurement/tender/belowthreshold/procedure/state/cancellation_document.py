from openprocurement.tender.core.procedure.context import get_request, get_cancellation
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.state.cancellation_document import CancellationDocumentStateMixing
from openprocurement.tender.belowthreshold.procedure.state.cancellation import BelowThresholdCancellationState


class BTCancellationDocumentState(CancellationDocumentStateMixing, BelowThresholdCancellationState):
    pass
