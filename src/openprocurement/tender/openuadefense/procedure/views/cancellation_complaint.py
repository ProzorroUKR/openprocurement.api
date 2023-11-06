from cornice.resource import resource
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)
from openprocurement.tender.openuadefense.procedure.state.cancellation_complaint import (
    OpenUADefenseCancellationComplaintState,
)


@resource(
    name="aboveThresholdUA.defense:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class OpenUADefenseCancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name="aboveThresholdUA.defense:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdUA.defense",
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class OpenUADefenseCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = OpenUADefenseCancellationComplaintState

