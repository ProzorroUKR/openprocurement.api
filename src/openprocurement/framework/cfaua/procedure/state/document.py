from openprocurement.api.procedure.state.base import BaseState
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.framework.cfaua.procedure.models.document import Document, PatchDocument, PostDocument
from openprocurement.framework.cfaua.procedure.validation import validate_related_item
from openprocurement.framework.core.procedure.state.document import FrameworkDocumentStateMixin


class AgreementDocumentState(FrameworkDocumentStateMixin, BaseState):
    post_data_model = PostDocument
    patch_data_model = PatchDocument
    data_model = Document

    item_name = "agreement"
    document_owner_item_name = "agreement"

    def validate_document_operation_allowed(self):
        status = self.request.validated["agreement"]["status"]
        if status != "active":
            raise_operation_error(
                self.request,
                f"Can't {OPERATIONS.get(self.request.method)} document in current ({status}) agreement status",
            )

    def validate_document_post(self, data):
        validate_related_item(data.get("relatedItem"), data["documentOf"])

    def validate_document_patch(self, before, after):
        validate_related_item(after.get("relatedItem"), after["documentOf"])
