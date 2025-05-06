from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.complaint_appeal_document import (
    CFAUAComplaintAppealDocumentState,
)
from openprocurement.tender.core.procedure.views.complaint_appeal_document import (
    BaseTenderComplaintAppealDocumentResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Complaint Appeal Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/appeals/{appeal_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender complaint appeals documents",
)
class CFAUAComplaintAppealDocumentResource(BaseTenderComplaintAppealDocumentResource):
    state_class = CFAUAComplaintAppealDocumentState
