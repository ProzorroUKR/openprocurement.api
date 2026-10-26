from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
from openprocurement.tender.arma.procedure.state.lot import (
    ComplexAssetLotState,
    SimpleAssetLotState,
)
from openprocurement.tender.core.procedure.views.lot import TenderLotResource


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="ARMA lots",
)
class LotResource(TenderLotResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetLotState,
        SIMPLE_ASSET_ARMA: SimpleAssetLotState,
    }
