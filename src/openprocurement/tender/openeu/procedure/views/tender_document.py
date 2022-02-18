from openprocurement.tender.openua.procedure.views.tender_document import UATenderDocumentResource
from cornice.resource import resource


@resource(
    name="aboveThresholdEU:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender EU related binary files (PDFs, etc.)",
)
class TenderEUDocumentResource(UATenderDocumentResource):
    pass
