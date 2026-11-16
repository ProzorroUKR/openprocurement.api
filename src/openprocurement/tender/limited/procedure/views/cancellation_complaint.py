from cornice.resource import resource

from openprocurement.api.constants import ProcurementMethodType
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)
from openprocurement.tender.limited.procedure.state.cancellation_complaints import (
    NegotiationCancellationComplaintState,
)


@resource(
    name="negotiation:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION,
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class NegotiationCancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name="negotiation:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION,
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class NegotiationCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = NegotiationCancellationComplaintState


@resource(
    name="negotiation.quick:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION_QUICK,
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class NegotiationQuickCancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name="negotiation.quick:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType=ProcurementMethodType.NEGOTIATION_QUICK,
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class NegotiationQuickCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = NegotiationCancellationComplaintState
