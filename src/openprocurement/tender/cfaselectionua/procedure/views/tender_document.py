from cornice.resource import resource

from openprocurement.tender.cfaselectionua.procedure.state.tender_document import (
    CFASelectionTenderDocumentState,
)
from openprocurement.tender.core.procedure.views.tender_document import (
    TenderDocumentResource,
)


@resource(
    name="closeFrameworkAgreementSelectionUA:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType="closeFrameworkAgreementSelectionUA",
    description="Tender closeFrameworkAgreementSelectionUA related binary files (PDFs, etc.)",
)
class CFASelectionTenderDocumentResource(TenderDocumentResource):
    state_class = CFASelectionTenderDocumentState
