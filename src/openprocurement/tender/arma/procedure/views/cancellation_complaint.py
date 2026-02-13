from cornice.resource import resource

from openprocurement.tender.arma.constants import COMPLEX_ASSET_ARMA
from openprocurement.tender.arma.procedure.state.cancellation_complaint import (
    CancellationComplaintState,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintWriteResource as BaseCancellationComplaintWriteResource,
)


@resource(
    name="complexAsset.arma:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class CancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name="complexAsset.arma:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=COMPLEX_ASSET_ARMA,
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
)
class CancellationComplaintWriteResource(BaseCancellationComplaintWriteResource):
    state_class = CancellationComplaintState
