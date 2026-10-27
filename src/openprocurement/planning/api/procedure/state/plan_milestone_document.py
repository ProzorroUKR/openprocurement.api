from openprocurement.planning.api.procedure.context import get_milestone, get_plan
from openprocurement.planning.api.procedure.models.document import (
    Document,
    PatchDocument,
    PostDocument,
)
from openprocurement.planning.api.procedure.state.plan_milestone import MilestoneState
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixin


class PlanMilestoneDocumentState(BaseDocumentStateMixin, MilestoneState):
    post_data_model = PostDocument
    patch_data_model = PatchDocument
    data_model = Document

    document_owner_item_name = "milestone"

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

    def document_on_post(self, data):
        super().document_on_post(data)
        self.milestone_always(get_milestone())
        self.always(get_plan())

    def document_on_patch(self, before, after):
        super().document_on_patch(before, after)
        self.milestone_always(get_milestone())
        self.always(get_plan())
