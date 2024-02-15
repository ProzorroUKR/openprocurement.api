from openprocurement.tender.core.procedure.state.award_complaint_document import (
    AwardComplaintDocumentState,
)
from openprocurement.tender.core.procedure.views.award import resolve_award
from openprocurement.tender.core.procedure.views.complaint import resolve_complaint
from openprocurement.tender.core.procedure.views.complaint_document import (
    BaseComplaintDocumentResource,
)
from openprocurement.tender.core.procedure.views.document import resolve_document


class AwardComplaintDocumentResource(BaseComplaintDocumentResource):
    state_class = AwardComplaintDocumentState

    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_award(request)
        resolve_complaint(request, context="award")
        resolve_document(request, self.item_name, self.container)
