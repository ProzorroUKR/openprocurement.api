# -*- coding: utf-8 -*-
from openprocurement.tender.core.utils import optendersresource
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.open.views.complaint_post_document import TenderComplaintPostDocumentResource


@optendersresource(
    name=f"{ABOVE_THRESHOLD}:Tender Cancellation Complaint Post Documents",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender cancellation complaint post documents",
)
class TenderCancellationComplaintPostDocumentResource(TenderComplaintPostDocumentResource):
    pass
