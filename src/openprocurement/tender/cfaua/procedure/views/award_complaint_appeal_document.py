from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.complaint_appeal_document import (
    CFAUAComplaintAppealDocumentState,
)
from openprocurement.tender.core.procedure.views.award_complaint_appeal_document import (
    BaseAwardComplaintAppealDocumentResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Award Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender award complaint appeal documents",
)
class CFAUAAwardComplaintAppealDocumentResource(BaseAwardComplaintAppealDocumentResource):
    state_class = CFAUAComplaintAppealDocumentState
