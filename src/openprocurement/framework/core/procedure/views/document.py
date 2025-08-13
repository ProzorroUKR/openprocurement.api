from openprocurement.framework.core.procedure.models.document import Document
from openprocurement.framework.core.procedure.serializers.document import (
    SubmissionDocumentSerializer,
)
from openprocurement.framework.core.procedure.state.document import (
    BaseFrameworkDocumentState,
    MilestoneDocumentState,
    QualificationDocumentState,
    SubmissionDocumentState,
)
from openprocurement.framework.core.procedure.utils import save_object
from openprocurement.framework.core.procedure.views.base import (
    BaseDocumentResource,
    FrameworkBaseResource,
)
from openprocurement.framework.core.procedure.views.change import resolve_change
from openprocurement.framework.core.procedure.views.contract import resolve_contract
from openprocurement.framework.core.procedure.views.milestone import resolve_milestone
from openprocurement.tender.core.procedure.documents import (
    get_file_docservice,
)
from openprocurement.tender.core.procedure.serializers.document import (
    DocumentSerializer,
)
from openprocurement.tender.core.procedure.views.document import (
    DocumentResourceMixin,
    resolve_document,
)


class CoreFrameworkDocumentResource(BaseDocumentResource):
    item_name = "framework"


class CoreSubmissionDocumentResource(BaseDocumentResource):
    item_name = "submission"
    serializer_class = SubmissionDocumentSerializer
    state_class = SubmissionDocumentState


class CoreQualificationDocumentResource(BaseDocumentResource):
    item_name = "qualification"
    state_class = QualificationDocumentState


class CoreMilestoneDocumentResource(FrameworkBaseResource, DocumentResourceMixin):
    item_name = "milestone"
    state_class = MilestoneDocumentState
    serializer_class = DocumentSerializer
    model_class = Document

    def __init__(self, request, context=None):
        super().__init__(request, context)
        resolve_contract(request)
        resolve_milestone(request)
        resolve_document(request, self.item_name, self.container)

    def save(self, **kwargs):
        return save_object(
            self.request,
            "agreement",
            modified=self.get_modified(),
            additional_obj_names=("milestone",),
            **kwargs,
        )

    def get_file(self):
        db_doc_id = self.request.validated[self.item_name]["id"]
        key = self.request.params.get("download")
        if not any(key in i["url"] for i in self.request.validated["documents"]):
            self.request.errors.add("url", "download", "Not Found")
            self.request.errors.status = 404
            return
        return get_file_docservice(self.request, db_doc_id, key)


class CoreFrameworkChangeDocumentResource(FrameworkBaseResource, DocumentResourceMixin):
    item_name = "change"
    state_class = BaseFrameworkDocumentState
    serializer_class = DocumentSerializer
    model_class = Document

    def __init__(self, request, context=None):
        super().__init__(request, context)
        resolve_change(request)
        resolve_document(request, self.item_name, self.container)

    def save(self, **kwargs):
        return save_object(
            self.request, "framework", modified=self.get_modified(), additional_obj_names=("change",), **kwargs
        )

    def get_file(self):
        db_doc_id = self.request.validated[self.item_name]["id"]
        key = self.request.params.get("download")
        if not any(key in i["url"] for i in self.request.validated["documents"]):
            self.request.errors.add("url", "download", "Not Found")
            self.request.errors.status = 404
            return
        return get_file_docservice(self.request, db_doc_id, key)
