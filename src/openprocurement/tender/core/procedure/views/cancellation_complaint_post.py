from openprocurement.tender.core.procedure.views.complaint import resolve_complaint
from openprocurement.tender.core.procedure.views.complaint_post import BaseComplaintPostResource, resolve_complaint_post
from openprocurement.tender.core.procedure.views.cancellation import resolve_cancellation


class BaseCancellationComplaintPostResource(BaseComplaintPostResource):
    item_name = "cancellation"

    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_cancellation(request)
        resolve_complaint(request, context="cancellation")
        resolve_complaint_post(request)
