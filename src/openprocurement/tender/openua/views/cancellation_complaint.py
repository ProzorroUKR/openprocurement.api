# -*- coding: utf-8 -*-

from openprocurement.tender.core.views.cancellation_complaint import TenderCancellationComplaintResource
from openprocurement.tender.core.utils import optendersresource


@optendersresource(
    name="aboveThresholdUA:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender cancellation complaints",
)
class TenderAboveThresholdUACancellationComplaintResource(TenderCancellationComplaintResource):
    """Tender AboveThresholdUA Cancellation Complaints """
