from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
from openprocurement.tender.arma.procedure.state.tender import (
    ComplexAssetTenderState,
    SimpleAssetTenderState,
)
from openprocurement.tender.core.procedure.views.chronograph import (
    TenderChronographResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Chronograph",
    path="/tenders/{tender_id}/chronograph",
    procurementMethodType=ARMAProcurementMethodType,
    description="Tender chronograph",
)
class ChronographResource(TenderChronographResource):
    state_classes = {
        ProcurementMethodType.COMPLEX_ASSET_ARMA: ComplexAssetTenderState,
        ProcurementMethodType.SIMPLE_ASSET_ARMA: SimpleAssetTenderState,
    }
