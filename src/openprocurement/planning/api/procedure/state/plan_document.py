from openprocurement.planning.api.procedure.context import get_plan
from openprocurement.planning.api.procedure.state.plan import PlanState
from openprocurement.tender.core.procedure.state.document import BaseDocumentStateMixing


class PlanDocumentState(BaseDocumentStateMixing, PlanState):
    allow_deletion = True

    def validate_document_post(self, data):
        super().validate_document_post(data)
        self._validate_plan_not_terminated(get_plan())

    def validate_document_patch(self, before, after):
        super().validate_document_patch(before, after)
        self._validate_plan_not_terminated(get_plan())
