from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_post_document import (
    BaseTenderComplaintPostDocumentResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Complaint Post Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender complaint post documents",
)
class CFAUAComplaintPostDocumentResource(BaseTenderComplaintPostDocumentResource):
    pass
