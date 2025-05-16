from openprocurement.tender.core.procedure.views.complaint import resolve_complaint
from openprocurement.tender.core.procedure.views.complaint_appeal import (
    BaseComplaintAppealResource,
    resolve_complaint_appeal,
)
from openprocurement.tender.core.procedure.views.qualification import (
    resolve_qualification,
)


class QualificationComplaintAppealResource(BaseComplaintAppealResource):
    item_name = "qualification"

    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_qualification(request)
        resolve_complaint(request, context="qualification")
        resolve_complaint_appeal(request)
