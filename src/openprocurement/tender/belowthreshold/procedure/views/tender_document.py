from cornice.resource import resource

from openprocurement.tender.belowthreshold.procedure.state.tender_document import (
    BelowThresholdTenderDocumentState,
)
from openprocurement.tender.core.procedure.views.tender_document import (
    TenderDocumentResource,
)


@resource(
    name="belowThreshold:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="belowThreshold",
    description="Tender related binary files (PDFs, etc.)",
)
class BelowThresholdTenderDocumentResource(TenderDocumentResource):
    state_class = BelowThresholdTenderDocumentState
