from cornice.resource import resource

from openprocurement.tender.competitiveordering.constants import COMPETITIVE_ORDERING
from openprocurement.tender.competitiveordering.procedure.state.cancellation_complaint import (
    COCancellationComplaintState,
)
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class COCancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name=f"{COMPETITIVE_ORDERING}:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=COMPETITIVE_ORDERING,
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class COCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = COCancellationComplaintState
