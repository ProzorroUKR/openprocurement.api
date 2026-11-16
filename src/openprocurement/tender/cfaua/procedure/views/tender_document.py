from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.cfaua.procedure.state.tender_document import (
    CFAUATenderDocumentState,
)
from openprocurement.tender.core.procedure.views.tender_document import TenderDocumentResource


@resource(
    name="closeFrameworkAgreementUA:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=ProcurementMethodType.CLOSE_FRAMEWORK_AGREEMENT_UA,
    description="Tender closeFrameworkAgreementUA related binary files (PDFs, etc.)",
)
class CFAUATenderDocumentResource(TenderDocumentResource):
    state_class = CFAUATenderDocumentState
