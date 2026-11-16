from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)
from openprocurement.tender.open.constants import OPEN_ROUTE_PREFIX
from openprocurement.tender.open.procedure.state.cancellation_complaint import (
    AboveThresholdCancellationComplaintState,
    AboveThresholdEUCancellationComplaintState,
    AboveThresholdUACancellationComplaintState,
    COCancellationComplaintState,
    DefenseCancellationComplaintState,
    OpenTenderingCancellationComplaintState,
    SimpleDefenseCancellationComplaintState,
)


@resource(
    name=f"{OPEN_ROUTE_PREFIX}:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    description="Tender cancellation complaints",
    request_method=["GET"],
    procurementMethodType=[
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.OPEN_TENDERING,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE,
        ProcurementMethodType.SIMPLE_DEFENSE,
        ProcurementMethodType.COMPETITIVE_ORDERING,
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
        ProcurementMethodType.ABOVE_THRESHOLD,
        ProcurementMethodType.ABOVE_THRESHOLD_UA,
        ProcurementMethodType.ABOVE_THRESHOLD_EU,
        ProcurementMethodType.OPEN_TENDERING,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE,
        ProcurementMethodType.SIMPLE_DEFENSE,
        ProcurementMethodType.COMPETITIVE_ORDERING,
    ],
)
class OpenCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_classes = {
        ProcurementMethodType.ABOVE_THRESHOLD: AboveThresholdCancellationComplaintState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA: AboveThresholdUACancellationComplaintState,
        ProcurementMethodType.ABOVE_THRESHOLD_EU: AboveThresholdEUCancellationComplaintState,
        ProcurementMethodType.OPEN_TENDERING: OpenTenderingCancellationComplaintState,
        ProcurementMethodType.ABOVE_THRESHOLD_UA_DEFENSE: DefenseCancellationComplaintState,
        ProcurementMethodType.SIMPLE_DEFENSE: SimpleDefenseCancellationComplaintState,
        ProcurementMethodType.COMPETITIVE_ORDERING: COCancellationComplaintState,
    }
