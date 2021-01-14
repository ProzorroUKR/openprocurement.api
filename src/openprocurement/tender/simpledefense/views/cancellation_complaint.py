# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource

from openprocurement.tender.openuadefense.views.cancellation_complaint import (
    TenderAboveThresholdUADefenseCancellationComplaintResource as BaseCancellationComplaintResource,
)


@optendersresource(
    name="simple.defense:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    description="Tender cancellation complaints",
)
class TenderSimpleDefCancellationComplaintResource(BaseCancellationComplaintResource):
    """Tender Simple Defense Cancellation Complaints """
