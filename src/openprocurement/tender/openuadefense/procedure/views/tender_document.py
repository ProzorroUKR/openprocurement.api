from cornice.resource import resource

from openprocurement.tender.openua.procedure.views.tender_document import (
    UATenderDocumentResource,
)


@resource(
    name="aboveThresholdUA.defense:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender UA.defense related binary files (PDFs, etc.)",
)
class UADefenseTenderDocumentResource(UATenderDocumentResource):
    pass
