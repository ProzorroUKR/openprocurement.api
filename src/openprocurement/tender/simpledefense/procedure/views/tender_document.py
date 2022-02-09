from openprocurement.tender.openuadefense.procedure.views.tender_document import UADefenseTenderDocumentResource
from cornice.resource import resource


@resource(
    name="simple.defense:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="simple.defense",
    description="Tender simple.defense related binary files (PDFs, etc.)",
)
class SimpleDefenseTenderDocumentResource(UADefenseTenderDocumentResource):
    pass
