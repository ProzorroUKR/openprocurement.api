from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.state.award_complaint import AwardComplaintState
from openprocurement.tender.core.procedure.views.award import resolve_award
from openprocurement.tender.core.procedure.views.complaint import (
    resolve_complaint,
    BaseComplaintGetResource,
    BaseComplaintWriteResource,
)
from openprocurement.tender.core.procedure.models.complaint import PostComplaintFromBid
from openprocurement.tender.core.procedure.validation import (
    unless_admins,
    validate_any_bid_owner,
    validate_input_data,
    validate_data_documents,
)
from openprocurement.api.utils import json_view


class AwardComplaintGetResource(BaseComplaintGetResource):
    item_name = "award"

    def __init__(self, request, context=None):
        TenderBaseResource.__init__(self, request, context)
        if context and request.matchdict:
            resolve_award(request)
            resolve_complaint(request, context="award")


class AwardComplaintWriteResource(BaseComplaintWriteResource):
    state_class = AwardComplaintState
    item_name = "award"

    def __init__(self, request, context=None):
        TenderBaseResource.__init__(self, request, context)
        if context and request.matchdict:
            resolve_award(request)
            resolve_complaint(request, context="award")

    @json_view(
        content_type="application/json",
        permission="create_complaint",
        validators=(
            unless_admins(
                validate_any_bid_owner(statuses=("active",))
            ),
            validate_input_data(PostComplaintFromBid),
            validate_data_documents(route_key="complaint_id", uid_key="id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()
