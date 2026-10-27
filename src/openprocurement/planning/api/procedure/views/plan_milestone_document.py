from cornice.resource import resource

from openprocurement.api.utils import json_view
from openprocurement.planning.api.procedure.models.document import (
    Document,
)
from openprocurement.planning.api.procedure.serializers.document import (
    DocumentSerializer,
)
from openprocurement.planning.api.procedure.state.plan_milestone_document import (
    PlanMilestoneDocumentState,
)
from openprocurement.planning.api.procedure.utils import save_plan
from openprocurement.planning.api.procedure.views.base import PlanBaseResource
from openprocurement.planning.api.procedure.views.plan_milestone import (
    resolve_milestone,
)
from openprocurement.tender.core.procedure.documents import get_file
from openprocurement.tender.core.procedure.views.document import (
    DocumentResourceMixin,
    resolve_document,
)


@resource(
    name="Plan Milestone Documents",
    collection_path="/plans/{plan_id}/milestones/{milestone_id}/documents",
    path="/plans/{plan_id}/milestones/{milestone_id}/documents/{document_id}",
    description="Plan milestone related binary files (PDFs, etc.)",
)
class PlanMilestoneDocumentResource(PlanBaseResource, DocumentResourceMixin):
    state_class = PlanMilestoneDocumentState
    serializer_class = DocumentSerializer
    model_class = Document
    item_name = "milestone"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        resolve_milestone(request)
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
        permission="update_milestone",
    )
    def collection_post(self):
        self.state.validate_document_post_request()
        return super().collection_post()

    @json_view(
        permission="update_milestone",
    )
    def put(self):
        self.state.validate_document_put_request()
        return super().put()

    @json_view(
        content_type="application/json",
        permission="update_milestone",
    )
    def patch(self):
        self.state.validate_document_patch_request()
        return super().patch()
