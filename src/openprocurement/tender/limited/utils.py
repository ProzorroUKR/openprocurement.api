from openprocurement.api.utils import get_now
from openprocurement.tender.core.utils import (
    check_cancellation_status,
    CancelTenderLot as BaseCancelTenderLot,
    check_complaint_statuses_at_complaint_period_end
)


def check_status(request):
    tender = request.validated["tender"]
    now = get_now()
    check_complaint_statuses_at_complaint_period_end(tender, now)
    check_cancellation_status(request)


class ReportingCancelTenderLot(BaseCancelTenderLot):
    def cancel_tender_method(self, request):
        tender = request.validated["tender"]
        tender.status = "cancelled"

    def cancel_lot(self, request, cancellation=None):
        raise NotImplementedError("N/A for this procedure")

