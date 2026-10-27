from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.submission import (
    SubmissionsResource,
)
from openprocurement.framework.ifi.constants import IFI_TYPE
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
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        content_type="application/json",
        permission="edit_submission",
    )
    def patch(self):
        return super().patch()
