from pyramid.security import ALL_PERMISSIONS, Allow, Everyone

from openprocurement.api.database import atomic_transaction
from openprocurement.api.utils import (
    request_fetch_agreement,
    request_fetch_framework,
    request_init_agreement,
    request_init_framework,
    request_init_qualification,
    request_init_submission,
)
from openprocurement.api.views.base import BaseResource
from openprocurement.framework.core.procedure.models.document import Document
from openprocurement.framework.core.procedure.state.document import (
    BaseFrameworkDocumentState,
)
from openprocurement.framework.core.procedure.state.framework import FrameworkState
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.utils import request_create_or_update_object
from openprocurement.tender.core.procedure.documents import get_file
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)
from openprocurement.tender.core.procedure.views.document import (
    DocumentResourceMixin,
    resolve_document,
)


class FrameworkBaseResource(BaseResource):  # TODO: make more specific classes
    state_class = FrameworkState

    def __acl__(self):
        acl = [
            (Allow, Everyone, "view_framework"),
            (Allow, "g:brokers", "create_framework"),
            (Allow, "g:framework_owner", "edit_framework"),
            (Allow, "g:brokers", "edit_framework"),
            (Allow, "g:Administrator", "edit_framework"),
            (Allow, "g:chronograph", "edit_framework"),
            # Submission permissions
            (Allow, "g:brokers", "create_submission"),
            (Allow, "g:chronograph", "edit_submission"),
            (Allow, "g:submission_owner", "edit_submission"),
            (Allow, "g:brokers", "edit_submission"),
            (Allow, "g:Administrator", "edit_submission"),
            # Qualification permissions
            (Allow, Everyone, "view_qualification"),
            (Allow, "g:bots", "create_qualification"),
            (Allow, "g:bots", "edit_qualification"),
            (Allow, "g:framework_owner", "edit_qualification"),
            (Allow, "g:brokers", "edit_qualification"),
            (Allow, "g:Administrator", "edit_qualification"),
            # Agreement permissions
            (Allow, "g:agreements", "create_agreement"),
            (Allow, "g:chronograph", "edit_agreement"),
            (Allow, "g:Administrator", "edit_agreement"),
            (Allow, "g:brokers", "edit_agreement"),
            # Question permissions
            (Allow, "g:brokers", "create_question"),
            (Allow, "g:brokers", "edit_question"),
            (Allow, "g:admins", ALL_PERMISSIONS),
        ]
        return acl

    def __init__(self, request, context=None):
        super().__init__(request, context)
        # init state class that handles framework business logic
        self.state = self.state_class(request)

        # https://github.com/Cornices/cornice/issues/479#issuecomment-388407385
        # init is called twice (with and without context), thanks to cornice.
        if not context:
            # getting framework, submission, qualification, agreement
            match_dict = request.matchdict
            if match_dict:
                self.fetch_all_objects()

    @staticmethod
    def fetch_object(request, match_dict, obj_name, obj_init_func):
        if match_dict.get(f"{obj_name}_id"):
            obj_init_func(request, getattr(request, f"{obj_name}_doc"))
            if request.method not in ("GET", "HEAD"):
                if "frameworkID" in request.validated[obj_name]:
                    framework_id = request.validated[obj_name].get("frameworkID")
                    request_fetch_framework(request, framework_id)
                if "agreementID" in request.validated[obj_name]:
                    agreement_id = request.validated[obj_name].get("agreementID")
                    request_fetch_agreement(request, agreement_id)

    def fetch_all_objects(self):
        self.fetch_object(self.request, self.request.matchdict, "framework", request_init_framework)
        self.fetch_object(self.request, self.request.matchdict, "qualification", request_init_qualification)
        self.fetch_object(self.request, self.request.matchdict, "submission", request_init_submission)
        self.fetch_object(self.request, self.request.matchdict, "agreement", request_init_agreement)

    def save_all_objects(self):
        with atomic_transaction():
            request_create_or_update_object(self.request, "framework")
            request_create_or_update_object(self.request, "qualification")
            request_create_or_update_object(self.request, "submission")
            request_create_or_update_object(self.request, "agreement")


class BaseDocumentResource(FrameworkBaseResource, DocumentResourceMixin):
    state_class = BaseFrameworkDocumentState
    serializer_class = DocumentSerializer
    model_class = Document
    item_name = "framework"

    def __init__(self, request, context=None):
        super().__init__(request, context)
        resolve_document(request, self.item_name, self.container)

    def save(self, **kwargs):
        return save_object(self.request, self.item_name, modified=self.get_modified(), **kwargs)

    def get_file(self):
        return get_file(self.request, item_name=self.item_name)
