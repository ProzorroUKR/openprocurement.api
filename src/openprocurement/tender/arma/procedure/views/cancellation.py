from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.arma.constants import ARMA_ROUTE_PREFIX, ARMAProcurementMethodType
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
    procurementMethodType=ARMAProcurementMethodType,
    description="Tender cancellations",
)
class CancellationResource(BaseCancellationResource):
    state_classes = {
        ProcurementMethodType.COMPLEX_ASSET_ARMA: ComplexAssetCancellationState,
        ProcurementMethodType.SIMPLE_ASSET_ARMA: SimpleAssetCancellationState,
    }
