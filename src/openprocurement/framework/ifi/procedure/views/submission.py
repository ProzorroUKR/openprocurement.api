from cornice.resource import resource

from openprocurement.api.procedure.validation import (
    unless_administrator,
    validate_config_data,
    validate_data_documents,
    validate_input_data,
    validate_item_owner,
    validate_patch_data,
)
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.models.submission import (
    PatchSubmission,
    SubmissionConfig,
)
from openprocurement.framework.core.procedure.validation import (
    validate_action_in_not_allowed_framework_status,
    validate_activate_submission,
    validate_framework,
    validate_operation_submission_in_not_allowed_period,
    validate_post_submission_with_active_contract,
    validate_submission_framework,
    validate_submission_status,
    validate_update_submission_in_not_allowed_status,
)
from openprocurement.framework.core.procedure.views.submission import (
    SubmissionsResource,
)
from openprocurement.framework.ifi.constants import IFI_TYPE
from openprocurement.framework.ifi.procedure.models.submission import (
    PostSubmission,
    Submission,
)
from openprocurement.framework.ifi.procedure.state.framework import IFIFrameworkState


@resource(
    name=f"{IFI_TYPE}:Submissions",
    collection_path="/submissions",
    path="/submissions/{submission_id}",
    description=f"{IFI_TYPE} submissions",
    submissionType=IFI_TYPE,
    accept="application/json",
)
class IFISubmissionResource(SubmissionsResource):
    state_class = IFIFrameworkState

    @json_view(
        content_type="application/json",
        permission="create_submission",
        validators=(
            validate_input_data(PostSubmission),
            validate_config_data(SubmissionConfig),
            validate_framework,
            validate_operation_submission_in_not_allowed_period,
            validate_action_in_not_allowed_framework_status("submission"),
            validate_post_submission_with_active_contract,
            validate_data_documents(route_key="submission_id"),
        ),
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        validators=(
            unless_administrator(validate_item_owner("submission")),
            validate_input_data(PatchSubmission),
            validate_submission_framework,
            validate_update_submission_in_not_allowed_status,
            validate_submission_status,
            validate_activate_submission,
            validate_operation_submission_in_not_allowed_period,
            validate_action_in_not_allowed_framework_status("submission"),
            validate_patch_data(Submission, item_name="submission"),
        ),
        permission="edit_submission",
    )
    def patch(self):
        return super().patch()
