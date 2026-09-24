from cornice.resource import resource

from openprocurement.tender.core.procedure.views.tender_document import TenderDocumentResource
from openprocurement.tender.open.procedure.state.tender_document import AboveThresholdTenderDocumentState


@resource(
    name="esco:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="esco",
    description="Tender ESCO related binary files (PDFs, etc.)",
)
class ESCOTenderDocumentResource(TenderDocumentResource):
    state_class = AboveThresholdTenderDocumentState
