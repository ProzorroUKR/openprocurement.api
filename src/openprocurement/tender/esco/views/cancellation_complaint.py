# -*- coding: utf-8 -*-

from openprocurement.tender.core.views.cancellation_complaint import TenderCancellationComplaintResource
from openprocurement.tender.core.utils import optendersresource


@optendersresource(
    name="esco:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    description="Tender cancellation complaints",
)
class TenderESCOCancellationComplaintResource(TenderCancellationComplaintResource):
    """Tender ESCO Cancellation Complaints """
