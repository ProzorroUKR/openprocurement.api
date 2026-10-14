from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
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
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender chronograph",
)
class ChronographResource(TenderChronographResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetTenderState,
        SIMPLE_ASSET_ARMA: SimpleAssetTenderState,
    }
