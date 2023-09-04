from openprocurement.tender.core.procedure.views.complaint import resolve_complaint
from openprocurement.tender.core.procedure.views.complaint_post import BaseComplaintPostResource, resolve_complaint_post
from openprocurement.tender.core.procedure.views.award import resolve_award


class BaseAwardComplaintPostResource(BaseComplaintPostResource):
    item_name = "award"

    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_award(request)
        resolve_complaint(request, context="award")
        resolve_complaint_post(request)
