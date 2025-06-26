from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.competitiveordering.procedure.state.tender import (
    COTenderState,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.core.procedure.state.question import (
    TenderQuestionStateMixin,
)


class COTenderQuestionStateMixin(TenderQuestionStateMixin):
    def validate_question_operation(self, tender, question):
        super().validate_question_operation(tender, question)
        if tender["status"] != "active.tendering":
            raise_operation_error(
                get_request(),
                "Can't update question in current ({}) tender status".format(tender["status"]),
            )


class COTenderQuestionState(COTenderQuestionStateMixin, COTenderState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
