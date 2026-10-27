from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.core.procedure.views.document import (
    CoreFrameworkDocumentResource,
)
from openprocurement.framework.electroniccatalogue.constants import (
    ELECTRONIC_CATALOGUE_TYPE,
)


@resource(
    name=f"{ELECTRONIC_CATALOGUE_TYPE}:Framework Documents",
    collection_path="/frameworks/{framework_id}/documents",
    path="/frameworks/{framework_id}/documents/{document_id}",
    frameworkType=ELECTRONIC_CATALOGUE_TYPE,
    description="Framework related binary files (PDFs, etc.)",
)
class FrameworkDocumentResource(CoreFrameworkDocumentResource):
    @json_view(permission="view_framework")
    def collection_get(self):
        return super().collection_get()

    @json_view(permission="view_framework")
    def get(self):
        return super().get()

    @json_view(
        permission="edit_framework",
    )
    def collection_post(self):
        return super().collection_post()

    @json_view(
        permission="edit_framework",
    )
    def put(self):
        return super().put()

    @json_view(
        content_type="application/json",
        permission="edit_framework",
    )
    def patch(self):
        return super().patch()
