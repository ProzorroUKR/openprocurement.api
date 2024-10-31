from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.qualification_complaint_document import (
    CFAUAQualificationComplaintDocumentState,
)
from openprocurement.tender.core.procedure.views.qualification_complaint_document import (
    QualificationComplaintDocumentResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Qualification Complaint Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender qualification complaint documents",
)
class CFAUAQualificationComplaintDocumentResource(QualificationComplaintDocumentResource):
    state_class = CFAUAQualificationComplaintDocumentState
