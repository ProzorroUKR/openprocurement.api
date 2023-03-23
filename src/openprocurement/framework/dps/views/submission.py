from openprocurement.api.utils import json_view
from openprocurement.framework.core.utils import submissionsresource
from openprocurement.framework.core.views.submission import CoreSubmissionResource
from openprocurement.framework.core.validation import (
    validate_patch_submission_data,
    validate_operation_submission_in_not_allowed_period,
    validate_submission_status,
    validate_update_submission_in_not_allowed_status,
    validate_activate_submission,
    validate_action_in_not_allowed_framework_status,
)
from openprocurement.framework.dps.constants import DPS_TYPE


@submissionsresource(
    name=f"{DPS_TYPE}:Submissions",
    path="/submissions/{submission_id}",
    submissionType=DPS_TYPE,
    description="Submissions",
)
class SubmissionResource(CoreSubmissionResource):
    @json_view(
        content_type="application/json",
        validators=(
            validate_patch_submission_data,
            validate_operation_submission_in_not_allowed_period,
            validate_update_submission_in_not_allowed_status,
            validate_action_in_not_allowed_framework_status("submission"),
            validate_submission_status,
            validate_activate_submission,
        ),
        permission="edit_submission",
    )
    def patch(self):
        return super().patch()
