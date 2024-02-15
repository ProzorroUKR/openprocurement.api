from cornice.resource import resource

from openprocurement.tender.openua.procedure.views.tender_document import (
    UATenderDocumentResource,
)


@resource(
    name="esco:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="esco",
    description="Tender ESCO related binary files (PDFs, etc.)",
)
class ESCOTenderDocumentResource(UATenderDocumentResource):
    pass
