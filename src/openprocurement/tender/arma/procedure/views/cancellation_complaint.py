from cornice.resource import resource

from openprocurement.tender.arma.constants import (
    ARMA_PROCUREMENT_METHOD_TYPES,
    ARMA_ROUTE_PREFIX,
    COMPLEX_ASSET_ARMA,
    SIMPLE_ASSET_ARMA,
)
from openprocurement.tender.arma.procedure.state.cancellation_complaint import (
    ComplexAssetCancellationComplaintState,
    SimpleAssetCancellationComplaintState,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintWriteResource as BaseCancellationComplaintWriteResource,
)


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class CancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name=f"{ARMA_ROUTE_PREFIX}:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=ARMA_PROCUREMENT_METHOD_TYPES,
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
)
class CancellationComplaintWriteResource(BaseCancellationComplaintWriteResource):
    state_classes = {
        COMPLEX_ASSET_ARMA: ComplexAssetCancellationComplaintState,
        SIMPLE_ASSET_ARMA: SimpleAssetCancellationComplaintState,
    }
