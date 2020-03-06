# -*- coding: utf-8 -*-

from openprocurement.tender.core.views.cancellation_complaint import TenderCancellationComplaintResource
from openprocurement.tender.core.utils import optendersresource


@optendersresource(
    name="negotiation:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation",
    description="Tender cancellation complaints",
)
class TenderNegotiationCancellationComplaintResource(TenderCancellationComplaintResource):
    """Tender Negotiation Cancellation Complaints """

    def recalculate_tender_periods(self):
        pass


@optendersresource(
    name="negotiation.quick:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation.quick",
    description="Tender cancellation complaints",
)
class TenderNegotiationQuickCancellationComplaintResource(TenderCancellationComplaintResource):
    """Tender Negotiation Quick Cancellation Complaints """

    def recalculate_tender_periods(self):
        pass
