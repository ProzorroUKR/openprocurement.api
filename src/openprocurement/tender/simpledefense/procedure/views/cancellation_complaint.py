from cornice.resource import resource
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)
from openprocurement.tender.simpledefense.procedure.state.cancellation_complaint import (
    SimpleDefenseCancellationComplaintState,
)


@resource(
    name="simple.defense:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class SimpleDefenseCancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name="simple.defense:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="simple.defense",
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class SimpleDefenseCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = SimpleDefenseCancellationComplaintState
