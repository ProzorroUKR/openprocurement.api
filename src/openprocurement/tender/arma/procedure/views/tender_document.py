from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
from openprocurement.tender.arma.procedure.state.tender_document import (
    ComplexAssetTenderDocumentState,
    SimpleAssetTenderDocumentState,
)
from openprocurement.tender.core.procedure.views.tender_document import (
    TenderDocumentResource as BaseTenderDocumentResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Documents",
    collection_path="/tenders/{tender_id}/documents",
    path="/tenders/{tender_id}/documents/{document_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender related binary files (PDFs, etc.)",
)
class TenderDocumentResource(BaseTenderDocumentResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetTenderDocumentState,
        SIMPLE_ASSET_ARMA: SimpleAssetTenderDocumentState,
    }
