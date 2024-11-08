from cornice.resource import resource

from openprocurement.tender.core.procedure.views.award_complaint_document import (
    AwardComplaintDocumentResource,
)
from openprocurement.tender.requestforproposal.procedure.state.award_complaint_document import (
    BTAwardComplaintDocumentState,
)


@resource(
    name="requestForProposal:Tender Award Complaint Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="requestForProposal",
    description="Tender award complaint documents",
)
class RequestForProposalAwardComplaintDocumentResource(AwardComplaintDocumentResource):
    state_class = BTAwardComplaintDocumentState
