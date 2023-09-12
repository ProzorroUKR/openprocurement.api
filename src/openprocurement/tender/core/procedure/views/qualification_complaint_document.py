from openprocurement.tender.core.procedure.views.document import resolve_document
from openprocurement.tender.core.procedure.views.qualification import resolve_qualification
from openprocurement.tender.core.procedure.views.complaint_document import BaseComplaintDocumentResource
from openprocurement.tender.core.procedure.views.complaint import resolve_complaint
from openprocurement.tender.core.procedure.state.qualification_complaint_document import (
    QualificationComplaintDocumentState,
)


class QualificationComplaintDocumentResource(BaseComplaintDocumentResource):
    state_class = QualificationComplaintDocumentState

    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_qualification(request)
        resolve_complaint(request, context="qualification")
        resolve_document(request, self.item_name, self.container)
