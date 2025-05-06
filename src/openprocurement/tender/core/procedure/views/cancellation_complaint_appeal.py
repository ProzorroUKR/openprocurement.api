from openprocurement.tender.core.procedure.views.cancellation import (
    resolve_cancellation,
)
from openprocurement.tender.core.procedure.views.complaint import resolve_complaint
from openprocurement.tender.core.procedure.views.complaint_appeal import (
    BaseComplaintAppealResource,
    resolve_complaint_appeal,
)


class BaseCancellationComplaintAppealResource(BaseComplaintAppealResource):
    item_name = "cancellation"

    def __init__(self, request, context=None):
        super().__init__(request, context)  # resolve tender
        resolve_cancellation(request)
        resolve_complaint(request, context="cancellation")
        resolve_complaint_appeal(request)
