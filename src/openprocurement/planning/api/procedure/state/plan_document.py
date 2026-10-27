from openprocurement.planning.api.procedure.context import get_plan
from openprocurement.planning.api.procedure.models.document import (
    Document,
    PatchDocument,
    PostDocument,
)
from openprocurement.planning.api.procedure.state.plan import PlanState
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixin


class PlanDocumentState(BaseDocumentStateMixin, PlanState):
    post_data_model = PostDocument
    patch_data_model = PatchDocument
    data_model = Document

    document_owner_item_name = "plan"
    allow_deletion = True

    def validate_document_patch_request(self):
        self.validate_document_owner(self.document_update_owner_exempt_roles)
        self.validate_patch_input_data(self.get_patch_data_model())
        self.validate_patch_data_simple(self.get_data_model(), item_name="document")

    def validate_document_post(self, data):
        super().validate_document_post(data)
        self._validate_plan_not_terminated(get_plan())

    def validate_document_patch(self, before, after):
        super().validate_document_patch(before, after)
        self._validate_plan_not_terminated(get_plan())
