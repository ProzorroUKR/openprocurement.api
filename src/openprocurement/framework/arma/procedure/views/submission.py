from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.api.utils import json_view
from openprocurement.framework.arma.procedure.state.framework import ARMAFrameworkState
from openprocurement.framework.core.procedure.views.submission import (
    SubmissionsResource,
)


@resource(
    name=f"{FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY}:Submissions",
    collection_path="/submissions",
    path="/submissions/{submission_id}",
    description=f"{FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY} submissions",
    submissionType=FrameworkType.ASSET_RECOVERY_MANAGEMENT_AGENCY,
    accept="application/json",
)
class ARMASubmissionResource(SubmissionsResource):
    state_class = ARMAFrameworkState

    @json_view(
        content_type="application/json",
        permission="create_submission",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_submission",
    )
    def patch(self):
        return super().patch()
