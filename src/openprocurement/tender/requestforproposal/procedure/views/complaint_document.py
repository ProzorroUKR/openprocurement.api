from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_document import (
    TenderComplaintDocumentResource,
)
from openprocurement.tender.requestforproposal.procedure.state.complaint_document import (
    BTComplaintDocumentState,
)


@resource(
    name="requestForProposal:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="requestForProposal",
    description="Tender complaint documents",
)
class RequestForProposalComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = BTComplaintDocumentState
