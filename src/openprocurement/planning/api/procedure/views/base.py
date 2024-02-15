from pyramid.security import Allow, Everyone, ALL_PERMISSIONS

from openprocurement.api.utils import request_init_plan
from openprocurement.api.views.base import BaseResource
from openprocurement.planning.api.procedure.models.document import Document
from openprocurement.planning.api.procedure.serializers.document import DocumentSerializer
from openprocurement.planning.api.procedure.state.plan import PlanState
from openprocurement.planning.api.procedure.state.plan_document import PlanDocumentState
from openprocurement.planning.api.procedure.utils import save_plan
from openprocurement.tender.core.procedure.documents import get_file
from openprocurement.tender.core.procedure.views.document import resolve_document, DocumentResourceMixin


class PlanBaseResource(BaseResource):
    state_class = PlanState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_listing"),
            (Allow, Everyone, "view_plan"),
            (Allow, "g:brokers", "create_plan"),
            (Allow, "g:brokers", "edit_plan"),
            (Allow, "g:brokers", "upload_plan_documents"),
            (Allow, "g:brokers", "create_tender_from_plan"),
            (Allow, "g:brokers", "post_plan_milestone"),
            (Allow, "g:brokers", "update_milestone"),
            (Allow, "g:Administrator", "edit_plan"),
            (Allow, "g:Administrator", "revision_plan"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        # init state class that handles plan business logic
        self.state = self.state_class(request)

        # https://github.com/Cornices/cornice/issues/479#issuecomment-388407385
        # init is called twice (with and without context), thanks to cornice.
        if not context:
            # getting plan
            match_dict = request.matchdict
            if match_dict and match_dict.get("plan_id"):
                request_init_plan(request, request.plan_doc)


class BaseDocumentResource(PlanBaseResource, DocumentResourceMixin):
    state_class = PlanDocumentState
    serializer_class = DocumentSerializer
    model_class = Document
    item_name = "plan"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        resolve_document(request, self.item_name, self.container)

    def save(self, **kwargs):
        return save_plan(self.request, modified=self.get_modified(), **kwargs)

    def get_file(self):
        return get_file(self.request, item_name=self.item_name)
