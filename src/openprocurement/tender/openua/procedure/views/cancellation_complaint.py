from cornice.resource import resource
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)
from openprocurement.tender.openua.procedure.state.cancellation_complaint import OpenUACancellationComplaintState


@resource(
    name="aboveThresholdUA:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class OpenUACancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name="aboveThresholdUA:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA",
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class OpenUACancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = OpenUACancellationComplaintState
