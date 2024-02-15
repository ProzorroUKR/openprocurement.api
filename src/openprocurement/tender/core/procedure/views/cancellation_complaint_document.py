from openprocurement.tender.core.procedure.state.cancellation_complaint_document import (
    CancellationComplaintDocumentState,
)
from openprocurement.tender.core.procedure.views.cancellation import (
    resolve_cancellation,
)
from openprocurement.tender.core.procedure.views.complaint import resolve_complaint
from openprocurement.tender.core.procedure.views.complaint_document import (
    BaseComplaintDocumentResource,
)
from openprocurement.tender.core.procedure.views.document import resolve_document


class CancellationComplaintDocumentResource(BaseComplaintDocumentResource):
    state_class = CancellationComplaintDocumentState

    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_cancellation(request)
        resolve_complaint(request, context="cancellation")
        resolve_document(request, self.item_name, self.container)
