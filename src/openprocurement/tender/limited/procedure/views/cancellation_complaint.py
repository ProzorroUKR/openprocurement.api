from cornice.resource import resource
from openprocurement.tender.core.procedure.views.cancellation_complaint import (
    CancellationComplaintGetResource,
    CancellationComplaintWriteResource,
)
from openprocurement.tender.limited.procedure.state.cancellation_complaints import (
    NegotiationCancellationComplaintState,
)
from openprocurement.tender.core.procedure.models.complaint import PostCancellationComplaint
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_data_documents,
)
from openprocurement.api.utils import json_view


@resource(
    name="negotiation:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation",
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class NegotiationCancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name="negotiation:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation",
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class NegotiationCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = NegotiationCancellationComplaintState

    @json_view(
        content_type="application/json",
        permission="create_complaint",
        validators=(
            validate_input_data(PostCancellationComplaint),
            validate_data_documents(route_key="complaint_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()


@resource(
    name="negotiation.quick:Tender Cancellation Complaints Get",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation.quick",
    description="Tender cancellation complaints",
    request_method=["GET"],
)
class NegotiationQuickCancellationClaimAndComplaintGetResource(CancellationComplaintGetResource):
    pass


@resource(
    name="negotiation.quick:Tender Cancellation Complaints",
    collection_path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints",
    path="/tenders/{tender_id}/cancellations/{cancellation_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation.quick",
    description="Tender cancellation complaints",
    request_method=["POST", "PATCH"],
    # complaintType="complaint",  you cannot set a different complaintType for Cancellation Complaint
)
class NegotiationQuickCancellationComplaintWriteResource(CancellationComplaintWriteResource):
    state_class = NegotiationCancellationComplaintState

    @json_view(
        content_type="application/json",
        permission="create_complaint",
        validators=(
                validate_input_data(PostCancellationComplaint),
                validate_data_documents(route_key="complaint_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()
