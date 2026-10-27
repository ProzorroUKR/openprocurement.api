from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.document import (
    CoreSubmissionDocumentResource,
)
from openprocurement.framework.dps.constants import DPS_TYPE


@resource(
    name=f"{DPS_TYPE}:Submission Documents",
    collection_path="/submissions/{submission_id}/documents",
    path="/submissions/{submission_id}/documents/{document_id}",
    description="Submission related binary files (PDFs, etc.)",
    submissionType=DPS_TYPE,
)
class SubmissionDocumentResource(CoreSubmissionDocumentResource):
    @json_view(
        permission="view_framework",
    )
    def collection_get(self):
        return super().collection_get()

    @json_view(
        permission="view_framework",
    )
    def get(self):
        return super().get()

    @json_view(
        permission="edit_submission",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        permission="edit_submission",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        permission="edit_submission",
    )
    def patch(self):
        return super().patch()
