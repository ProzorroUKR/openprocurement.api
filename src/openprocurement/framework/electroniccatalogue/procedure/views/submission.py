from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.submission import (
    SubmissionsResource,
)
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)
from openprocurement.framework.electroniccatalogue.procedure.state.framework import (
    ElectronicDialogueFrameworkState,
)


@resource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Submissions",
    collection_path="/submissions",
    path="/submissions/{submission_id}",
    description=f"{ELECTRONIC_CATALOGUE_TYPE} submissions",
    submissionType=ELECTRONIC_CATALOGUE_TYPE,
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
