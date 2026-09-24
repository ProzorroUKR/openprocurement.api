from cornice.resource import resource

from openprocurement.tender.core.procedure.views.tender_document import (
    TenderDocumentResource,
)
from openprocurement.tender.requestforproposal.procedure.state.tender_document import (
    RequestForProposalTenderDocumentState,
)


@resource(
    name="requestForProposal:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="requestForProposal",
    description="Tender related binary files (PDFs, etc.)",
)
class RequestForProposalTenderDocumentResource(TenderDocumentResource):
    state_class = RequestForProposalTenderDocumentState
