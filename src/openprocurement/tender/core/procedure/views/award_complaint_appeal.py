from openprocurement.tender.core.procedure.views.award import resolve_award
from openprocurement.tender.core.procedure.views.complaint import resolve_complaint
from openprocurement.tender.core.procedure.views.complaint_appeal import (
    BaseComplaintAppealResource,
    resolve_complaint_appeal,
)


class BaseAwardComplaintAppealResource(BaseComplaintAppealResource):
    item_name = "award"

    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_award(request)
        resolve_complaint(request, context="award")
        resolve_complaint_appeal(request)
