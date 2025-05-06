from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.complaint_appeal_document import (
    CFAUAComplaintAppealDocumentState,
)
from openprocurement.tender.core.procedure.views.qualification_complaint_appeal_document import (
    QualificationComplaintAppealDocumentResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Qualification Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/qualifications/{qualification_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender qualification complaint appeal documents",
)
class CFAUAQualificationComplaintAppealDocumentResource(QualificationComplaintAppealDocumentResource):
    state_class = CFAUAComplaintAppealDocumentState
