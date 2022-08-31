# -*- coding: utf-8 -*-

from openprocurement.tender.core.views.cancellation_complaint import TenderCancellationComplaintResource
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD


@optendersresource(
    name=f"{ABOVE_THRESHOLD}:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender cancellation complaints",
)
class TenderAboveThresholdCancellationComplaintResource(TenderCancellationComplaintResource):
    """Tender AboveThreshold Cancellation Complaints """
