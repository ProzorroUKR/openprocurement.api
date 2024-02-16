from cornice.resource import resource

from openprocurement.tender.openua.procedure.views.tender_document import (
    UATenderDocumentResource,
)


@resource(
    name="closeFrameworkAgreementUA:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementUA",
    description="Tender closeFrameworkAgreementUA related binary files (PDFs, etc.)",
)
class CFAUATenderDocumentResource(UATenderDocumentResource):
    pass
