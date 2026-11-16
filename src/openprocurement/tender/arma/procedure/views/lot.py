from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
from openprocurement.tender.arma.procedure.state.lot import (
    ComplexAssetLotState,
    SimpleAssetLotState,
)
from openprocurement.tender.core.procedure.views.lot import TenderLotResource


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Lots",
    collection_path="/tenders/{tender_id}/lots",
    path="/tenders/{tender_id}/lots/{lot_id}",
    procurementMethodType=ARMAProcurementMethodType,
    description="ARMA lots",
)
class LotResource(TenderLotResource):
    state_classes = {
        ProcurementMethodType.COMPLEX_ASSET_ARMA: ComplexAssetLotState,
        ProcurementMethodType.SIMPLE_ASSET_ARMA: SimpleAssetLotState,
    }
