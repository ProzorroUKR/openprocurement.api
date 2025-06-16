from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.complaint_document import (
    COComplaintDocumentState,
)
from openprocurement.tender.core.procedure.views.complaint_document import (
    TenderComplaintDocumentResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Complaint Documents",
    collection_path="/tenders/{tender_id}/complaints/{complaint_id}/documents",
    path="/tenders/{tender_id}/complaints/{complaint_id}/documents/{document_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender complaint documents",
)
class COComplaintDocumentResource(TenderComplaintDocumentResource):
    state_class = COComplaintDocumentState
