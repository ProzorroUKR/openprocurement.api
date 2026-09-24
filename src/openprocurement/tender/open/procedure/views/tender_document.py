from cornice.resource import resource

from openprocurement.tender.core.procedure.views.tender_document import (
    TenderDocumentResource,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.open.procedure.state.tender_document import (
    OpenTenderDocumentState,
)


@resource(
    name=f"{ABOVE_THRESHOLD}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=ABOVE_THRESHOLD,
    description="Tender related binary files (PDFs, etc.)",
)
class UATenderDocumentResource(TenderDocumentResource):
    state_class = OpenTenderDocumentState
