from openprocurement.tender.core.procedure.views.complaint import resolve_complaint
from openprocurement.tender.core.procedure.views.complaint_appeal import (
    resolve_complaint_appeal,
)
from openprocurement.tender.core.procedure.views.complaint_appeal_document import (
    BaseComplaintAppealDocumentResource,
)
from openprocurement.tender.core.procedure.views.document import resolve_document
from openprocurement.tender.core.procedure.views.qualification import (
    resolve_qualification,
)


class QualificationComplaintAppealDocumentResource(BaseComplaintAppealDocumentResource):
    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_qualification(request)
        resolve_complaint(request, context="qualification")
        resolve_complaint_appeal(request)
        resolve_document(request, self.item_name, self.container)
