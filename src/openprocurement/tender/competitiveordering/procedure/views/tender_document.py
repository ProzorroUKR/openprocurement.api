from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.tender_document import (
    COTenderDocumentState,
)
from openprocurement.tender.core.procedure.views.tender_document import (
    TenderDocumentResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender related binary files (PDFs, etc.)",
)
class COTenderDocumentResource(TenderDocumentResource):
    state_class = COTenderDocumentState
