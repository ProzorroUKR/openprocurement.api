from cornice.resource import resource

from openprocurement.tender.core.procedure.views.complaint_document import (
    TenderComplaintDocumentResource,
)
from openprocurement.tender.open.procedure.state.complaint_document import (
    OpenComplaintDocumentState,
)


@resource(
    name="simple.defense:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType="simple.defense",
    description="Tender complaint documents",
)
class SimpleDefenseComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = OpenComplaintDocumentState
