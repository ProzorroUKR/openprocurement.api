from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.complaint_post_document import (
    CFAUAComplaintPostDocumentState,
)
from openprocurement.tender.core.procedure.views.qualification_complaint_post_document import (
    QualificationComplaintPostDocumentResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Qualification Complaint Post Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/posts/{post_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender qualification complaint post documents",
)
class CFAUAQualificationComplaintPostDocumentResource(QualificationComplaintPostDocumentResource):
    state_class = CFAUAComplaintPostDocumentState
