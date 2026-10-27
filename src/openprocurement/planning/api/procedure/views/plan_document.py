from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.planning.api.procedure.models.document import (
    Document,
)
from openprocurement.planning.api.procedure.serializers.document import (
    DocumentSerializer,
)
from openprocurement.planning.api.procedure.state.plan_document import PlanDocumentState
from openprocurement.planning.api.procedure.utils import save_plan
from openprocurement.planning.api.procedure.views.base import PlanBaseResource
from openprocurement.tender.core.procedure.documents import get_file
from openprocurement.tender.core.procedure.views.document import (
    DocumentResourceMixin,
    resolve_document,
)


@resource(
    name="Plan Documents",
    collection_path="/plans/{plan_id}/documents",
    path="/plans/{plan_id}/documents/{document_id}",
    description="Plan related binary files (PDFs, etc.)",
)
class PlanDocumentResource(PlanBaseResource, DocumentResourceMixin):
    state_class = PlanDocumentState
    serializer_class = DocumentSerializer
    model_class = Document
    item_name = "plan"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        resolve_document(request, self.item_name, self.container)

    def get_file(self):
        return get_file(self.request, item_name="plan")

    def save(self, **kwargs):
        return save_plan(self.request, modified=self.get_modified(), **kwargs)

    @json_view(permission="view_plan")
    def collection_get(self):
        return super().collection_get()

    @json_view(permission="view_plan")
    def get(self):
        return super().get()

    @json_view(
        permission="upload_plan_documents",
    )
    def collection_post(self):
        self.state.validate_document_post_request()
        return super().collection_post()

    @json_view(
        permission="upload_plan_documents",
    )
    def put(self):
        self.state.validate_document_put_request()
        return super().put()

    @json_view(
        content_type="application/json",
        permission="upload_plan_documents",
    )
    def patch(self):
        self.state.validate_document_patch_request()
        return super().patch()

    @json_view(
        content_type="application/json",
        permission="upload_plan_documents",
    )
    def delete(self):
        self.state.validate_document_delete_request()
        return super().delete()
