from cornice.resource import resource
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)
from openprocurement.tender.openeu.procedure.state.cancellation_complaint import OpenEUCancellationComplaintState


@resource(
    name="aboveThresholdEU:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class OpenEUCancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name="aboveThresholdEU:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="aboveThresholdEU",
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class OpenEUCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = OpenEUCancellationComplaintState
