from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
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
    procurementMethodType=ARMAProcurementMethodType,
    description="Tender related binary files (PDFs, etc.)",
)
class TenderDocumentResource(BaseTenderDocumentResource):
    state_classes = {
        ProcurementMethodType.COMPLEX_ASSET_ARMA: ComplexAssetTenderDocumentState,
        ProcurementMethodType.SIMPLE_ASSET_ARMA: SimpleAssetTenderDocumentState,
    }
