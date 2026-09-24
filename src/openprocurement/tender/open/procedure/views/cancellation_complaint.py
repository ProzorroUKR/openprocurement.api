from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)
from openprocurement.tender.open.constants import (
    ABOVE_THRESHOLD,
    ABOVE_THRESHOLD_EU,
    ABOVE_THRESHOLD_UA,
    ABOVE_THRESHOLD_UA_DEFENSE,
    COMPETITIVE_ORDERING,
    OPEN_ROUTE_PREFIX,
    SIMPLE_DEFENSE,
)
from openprocurement.tender.open.procedure.state.cancellation_complaint import (
    AboveThresholdCancellationComplaintState,
    AboveThresholdEUCancellationComplaintState,
    AboveThresholdUACancellationComplaintState,
    COCancellationComplaintState,
    DefenseCancellationComplaintState,
    SimpleDefenseCancellationComplaintState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    description="Tender cancellation complaints",
    request_method=["GET"],
    procurementMethodType=[
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        ABOVE_THRESHOLD_UA_DEFENSE,
        SIMPLE_DEFENSE,
        COMPETITIVE_ORDERING,
    ],
)
class OpenCancellationComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
    procurementMethodType=[
        ABOVE_THRESHOLD,
        ABOVE_THRESHOLD_UA,
        ABOVE_THRESHOLD_EU,
        ABOVE_THRESHOLD_UA_DEFENSE,
        SIMPLE_DEFENSE,
        COMPETITIVE_ORDERING,
    ],
)
class OpenCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_classes = {
        ABOVE_THRESHOLD: AboveThresholdCancellationComplaintState,
        ABOVE_THRESHOLD_UA: AboveThresholdUACancellationComplaintState,
        ABOVE_THRESHOLD_EU: AboveThresholdEUCancellationComplaintState,
        ABOVE_THRESHOLD_UA_DEFENSE: DefenseCancellationComplaintState,
        SIMPLE_DEFENSE: SimpleDefenseCancellationComplaintState,
        COMPETITIVE_ORDERING: COCancellationComplaintState,
    }
