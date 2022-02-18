from openprocurement.tender.openua.procedure.views.tender_document import UATenderDocumentResource
from cornice.resource import resource


@resource(
    name="closeFrameworkAgreementUA:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender closeFrameworkAgreementUA related binary files (PDFs, etc.)",
)
class CFAUATenderDocumentResource(UATenderDocumentResource):
    pass
