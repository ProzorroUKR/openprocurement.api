from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
from openprocurement.tender.arma.procedure.state.award_document import (
    ComplexAssetAwardDocumentState,
    SimpleAssetAwardDocumentState,
)
from openprocurement.tender.core.procedure.views.award_document import (
    BaseAwardDocumentResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Award Documents",
    collection_path="/tenders/{tender_id}/awards/{award_id}/documents",
    path="/tenders/{tender_id}/awards/{award_id}/documents/{document_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender award documents",
)
class TenderAwardDocumentResource(BaseAwardDocumentResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetAwardDocumentState,
        SIMPLE_ASSET_ARMA: SimpleAssetAwardDocumentState,
    }
