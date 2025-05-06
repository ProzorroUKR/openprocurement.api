from openprocurement.tender.core.procedure.views.cancellation import (
    resolve_cancellation,
)
from openprocurement.tender.core.procedure.views.complaint import resolve_complaint
from openprocurement.tender.core.procedure.views.complaint_appeal import (
    resolve_complaint_appeal,
)
from openprocurement.tender.core.procedure.views.complaint_appeal_document import (
    BaseComplaintAppealDocumentResource,
)
from openprocurement.tender.core.procedure.views.document import resolve_document


class BaseCancellationComplaintAppealDocumentResource(BaseComplaintAppealDocumentResource):
    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_cancellation(request)
        resolve_complaint(request, context="cancellation")
        resolve_complaint_appeal(request)
        resolve_document(request, self.item_name, self.container)
