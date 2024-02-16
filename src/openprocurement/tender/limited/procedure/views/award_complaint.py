from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    validate_data_documents,
    validate_input_data,
)
from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.models.complaint import PostAwardComplaint
from openprocurement.tender.core.procedure.views.award_complaint import (
    AwardComplaintGetResource,
    AwardComplaintWriteResource,
)
from openprocurement.tender.limited.procedure.state.award_complaint import (
    NegotiationAwardComplaintState,
)


@resource(
    name="negotiation:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation",
    request_method=["GET"],
    description="Tender negotiation award complaints get",
)
class NegotiationAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name="negotiation:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender negotiation award complaints",
)
class NegotiationAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_class = NegotiationAwardComplaintState

    @json_view(
        content_type="application/json",
        permission="create_complaint",
        validators=(
            validate_input_data(PostAwardComplaint),
            validate_data_documents(route_key="complaint_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()


@resource(
    name="negotiation.quick:Tender Award Complaints Get",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation.quick",
    request_method=["GET"],
    description="Tender negotiation.quick award complaints get",
)
class NegotiationQuickAwardClaimAndComplaintGetResource(AwardComplaintGetResource):
    pass


@resource(
    name="negotiation.quick:Tender Award Complaints",
    collection_path="/tenders/{tender_id}/awards/{award_id}/complaints",
    path="/tenders/{tender_id}/awards/{award_id}/complaints/{complaint_id}",
    procurementMethodType="negotiation.quick",
    request_method=["POST", "PATCH"],
    complaintType="complaint",
    description="Tender negotiation.quick award complaints",
)
class NegotiationQuickAwardComplaintWriteResource(AwardComplaintWriteResource):
    state_class = NegotiationAwardComplaintState

    @json_view(
        content_type="application/json",
        permission="create_complaint",
        validators=(
            validate_input_data(PostAwardComplaint),
            validate_data_documents(route_key="complaint_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()
