from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.tender_document import (
    TenderDocumentState,
)
from openprocurement.tender.core.procedure.views.tender_document import (
    TenderDocumentResource as BaseTenderDocumentResource,
)


@resource(
    name=f"{COMPLEX_ASSET_ARMA}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender related binary files (PDFs, etc.)",
)
class TenderDocumentResource(BaseTenderDocumentResource):
    state_class = TenderDocumentState
