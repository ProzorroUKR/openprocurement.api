from openprocurement.api.auth import ACCR_4
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDEUTenderDetailsState,
    CDUATenderDetailsState,
)
from openprocurement.tender.competitivedialogue.procedure.validation import validate_author
from openprocurement.tender.core.procedure.context import get_request, get_tender
from openprocurement.tender.openua.procedure.state.question import UATenderQuestionStateMixin


class CDTenderQuestionStateMixin(UATenderQuestionStateMixin):
    def validate_question_on_post(self, question):
        super().validate_question_on_post(question)
        self.validate_question_author(question)

    def validate_question_on_patch(self, before, question):
        super().validate_question_on_patch(before, question)
        self.validate_question_author(question)

    def validate_question_author(self, question):
        validate_author(get_request(), get_tender(), question, "question")


class CDEUTenderQuestionState(CDTenderQuestionStateMixin, CDEUTenderDetailsState):
    create_accreditations = (ACCR_4,)


class CDUATenderQuestionState(CDTenderQuestionStateMixin, CDUATenderDetailsState):
    create_accreditations = (ACCR_4,)
