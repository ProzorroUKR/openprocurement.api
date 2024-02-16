from openprocurement.tender.core.procedure.views.complaint import resolve_complaint
from openprocurement.tender.core.procedure.views.complaint_post import (
    resolve_complaint_post,
)
from openprocurement.tender.core.procedure.views.complaint_post_document import (
    BaseComplaintPostDocumentResource,
)
from openprocurement.tender.core.procedure.views.document import resolve_document
from openprocurement.tender.core.procedure.views.qualification import (
    resolve_qualification,
)


class QualificationComplaintPostDocumentResource(BaseComplaintPostDocumentResource):
    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_qualification(request)
        resolve_complaint(request, context="qualification")
        resolve_complaint_post(request)
        resolve_document(request, self.item_name, self.container)
