from openprocurement.api.auth import AccreditationLevel
from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDEUStage2TenderDetailsState,
    CDUAStage2TenderDetailsState,
)
from openprocurement.tender.competitivedialogue.procedure.validation import (
    validate_author,
)
from openprocurement.tender.core.procedure.context import get_request
from openprocurement.tender.openua.procedure.state.question import (
    UATenderQuestionStateMixin,
)


class CDStage2TenderQuestionStateMixin(UATenderQuestionStateMixin):
    def validate_question_on_patch(self, before, question):
        super().validate_question_on_patch(before, question)
        self.validate_question_author(question)

    def validate_question_author(self, question):
        validate_author(get_request(), get_tender(), question, "question")


class CDEUStage2TenderQuestionState(CDStage2TenderQuestionStateMixin, CDEUStage2TenderDetailsState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)


class CDUAStage2TenderQuestionState(CDStage2TenderQuestionStateMixin, CDUAStage2TenderDetailsState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
