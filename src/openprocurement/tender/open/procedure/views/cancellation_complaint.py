from cornice.resource import resource
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)
from openprocurement.tender.open.constants import ABOVE_THRESHOLD_GROUP_NAME, ABOVE_THRESHOLD_GROUP
from openprocurement.tender.open.procedure.state.cancellation_complaint import OpenCancellationComplaintState


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class OpenCancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name=f"{ABOVE_THRESHOLD_GROUP_NAME}:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=ABOVE_THRESHOLD_GROUP,
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class OpenCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = OpenCancellationComplaintState
