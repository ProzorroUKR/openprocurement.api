from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
from openprocurement.tender.arma.procedure.state.cancellation import (
    ComplexAssetCancellationState,
    SimpleAssetCancellationState,
)
from openprocurement.tender.core.procedure.views.cancellation import (
    BaseCancellationResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Cancellations",
    collection_path="/tenders/{tender_id}/cancellations",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender cancellations",
)
class CancellationResource(BaseCancellationResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetCancellationState,
        SIMPLE_ASSET_ARMA: SimpleAssetCancellationState,
    }
