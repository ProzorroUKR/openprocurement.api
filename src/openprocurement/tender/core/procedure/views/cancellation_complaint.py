from openprocurement.api.utils import json_view
from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintState,
)
from openprocurement.tender.core.procedure.views.base import TenderBaseResource
from openprocurement.tender.core.procedure.views.cancellation import resolve_cancellation
from openprocurement.tender.core.procedure.models.complaint import (
    PostCancellationComplaint,
    CancellationComplaint,
)
from openprocurement.tender.core.procedure.validation import (
    validate_input_data,
    validate_data_documents,
    unless_administrator,
    unless_bots,
    unless_reviewers,
    validate_any,
    validate_item_owner,
    validate_input_data_from_resolved_model,
    validate_patch_data,
)
from openprocurement.tender.core.procedure.views.complaint import (
    resolve_complaint,
    BaseComplaintWriteResource,
    BaseComplaintGetResource,
)


class CancellationComplaintGetResource(BaseComplaintGetResource):
    item_name = "cancellation"

    def __init__(self, request, context=None):
        TenderBaseResource.__init__(self, request, context)
        if context and request.matchdict:
            resolve_cancellation(request)
            resolve_complaint(request, context="cancellation")


class CancellationComplaintWriteResource(BaseComplaintWriteResource):
    state_class = CancellationComplaintState
    item_name = "cancellation"

    def __init__(self, request, context=None):
        TenderBaseResource.__init__(self, request, context)
        if context and request.matchdict:
            resolve_cancellation(request)
            resolve_complaint(request, context="cancellation")

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

    @json_view(
        content_type="application/json",
        validators=(
                unless_administrator(
                    unless_bots(
                        unless_reviewers(
                            validate_any(
                                validate_item_owner("tender"),
                                validate_item_owner("complaint"),
                            )
                        )
                    )
                ),
                validate_input_data_from_resolved_model(),
                validate_patch_data(CancellationComplaint, item_name="complaint"),
        ),
        permission="edit_complaint",
    )
    def patch(self):
        return super().patch()
