from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_post_document import (
    BaseTenderComplaintPostDocumentResource,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD


@resource(
    name="aboveThresholdUA:Tender Complaint Post Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender complaint post documents",
)
class OpenUAComplaintPostDocumentResource(BaseTenderComplaintPostDocumentResource):
    pass
