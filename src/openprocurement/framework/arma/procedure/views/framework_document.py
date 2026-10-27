from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.framework.arma.constants import ARMA_TYPE
from openprocurement.framework.core.procedure.views.document import (
    CoreFrameworkDocumentResource,
)


@resource(
    name=f"{ARMA_TYPE}:Framework Documents",
    collection_path="/frameworks/{framework_id}/documents",
    path="/frameworks/{framework_id}/documents/{document_id}",
    frameworkType=ARMA_TYPE,
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
