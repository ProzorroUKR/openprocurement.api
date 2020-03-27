
from openprocurement.tender.core.utils import check_cancellation_status, CancelTenderLot as BaseCancelTenderLot


def check_status(request):
    check_cancellation_status(request)


class ReportingCancelTenderLot(BaseCancelTenderLot):
    def cancel_tender_method(self, request):
        tender = request.validated["tender"]
        tender.status = "cancelled"

    def cancel_lot(self, request, cancellation=None):
        raise NotImplementedError("N/A for this procedure")

