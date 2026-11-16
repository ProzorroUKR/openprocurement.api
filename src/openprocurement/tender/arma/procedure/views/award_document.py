from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
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
    procurementMethodType=ARMAProcurementMethodType,
    description="Tender award documents",
)
class TenderAwardDocumentResource(BaseAwardDocumentResource):
    state_classes = {
        ProcurementMethodType.COMPLEX_ASSET_ARMA: ComplexAssetAwardDocumentState,
        ProcurementMethodType.SIMPLE_ASSET_ARMA: SimpleAssetAwardDocumentState,
    }
