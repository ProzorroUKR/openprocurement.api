from cornice.resource import resource

from openprocurement.tender.cfaua.procedure.state.award_complaint_document import (
    CFAUAAwardComplaintDocumentState,
)
from openprocurement.tender.core.procedure.views.award_complaint_document import (
    AwardComplaintDocumentResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender award complaint documents",
)
class CFAUAAwardComplaintDocumentResource(AwardComplaintDocumentResource):
    state_class = CFAUAAwardComplaintDocumentState
