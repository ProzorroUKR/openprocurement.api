from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.submission import (
    SubmissionsResource,
)
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.framework.dps.procedure.state.framework import DPSFrameworkState


@resource(
    name=f"{DPS_TYPE}:Submissions",
    collection_path="/submissions",
    path="/submissions/{submission_id}",
    description=f"{DPS_TYPE} submissions",
    submissionType=DPS_TYPE,
    accept="application/json",
)
class DPSSubmissionResource(SubmissionsResource):
    state_class = DPSFrameworkState

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
