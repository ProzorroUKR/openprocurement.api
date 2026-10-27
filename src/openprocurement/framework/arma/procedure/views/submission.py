from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.arma.procedure.state.framework import ARMAFrameworkState
from openprocurement.framework.core.procedure.views.submission import (
    SubmissionsResource,
)


@resource(
    name=f"{ARMA_TYPE}:Submissions",
    collection_path="/submissions",
    path="/submissions/{submission_id}",
    description=f"{ARMA_TYPE} submissions",
    submissionType=ARMA_TYPE,
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
