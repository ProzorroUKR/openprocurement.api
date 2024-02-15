from cornice.resource import resource

from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)
from openprocurement.tender.esco.procedure.state.cancellation_complaint import (
    ESCOCancellationComplaintState,
)


@resource(
    name="esco:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class ESCOCancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name="esco:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="esco",
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class ESCOCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = ESCOCancellationComplaintState
