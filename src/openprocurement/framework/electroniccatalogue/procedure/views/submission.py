from cornice.resource import resource

from openprocurement.api.constants import FrameworkType
from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.submission import (
    SubmissionsResource,
)
from openprocurement.framework.electroniccatalogue.procedure.state.framework import (
    ElectronicDialogueFrameworkState,
)


@resource(
    name=f"{FrameworkType.ELECTRONIC_CATALOGUE}:Submissions",
    collection_path="/submissions",
    path="/submissions/{submission_id}",
    description=f"{FrameworkType.ELECTRONIC_CATALOGUE} submissions",
    submissionType=FrameworkType.ELECTRONIC_CATALOGUE,
    accept="application/json",
)
class ElectronicCatalogueSubmissionResource(SubmissionsResource):
    state_class = ElectronicDialogueFrameworkState

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
