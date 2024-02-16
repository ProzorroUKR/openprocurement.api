from openprocurement.planning.api.procedure.context import get_milestone, get_plan
from openprocurement.planning.api.procedure.state.plan_milestone import MilestoneState
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing


class PlanMilestoneDocumentState(BaseDocumentStateMixing, MilestoneState):
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
