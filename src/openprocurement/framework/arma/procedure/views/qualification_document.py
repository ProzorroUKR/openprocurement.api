from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.core.procedure.views.document import (
    CoreQualificationDocumentResource,
)


@resource(
    name=f"{ARMA_TYPE}:Qualification Documents",
    collection_path="/qualifications/{qualification_id}/documents",
    path="/qualifications/{qualification_id}/documents/{document_id}",
    description="Qualification related binary files (PDFs, etc.)",
    qualificationType=ARMA_TYPE,
)
class QualificationDocumentResource(CoreQualificationDocumentResource):
    @json_view(permission="view_framework")
    def collection_get(self):
        return super().collection_get()

    @json_view(permission="view_framework")
    def get(self):
        return super().get()

    @json_view(
        permission="edit_qualification",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        permission="edit_qualification",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        permission="edit_qualification",
    )
    def patch(self):
        return super().patch()
