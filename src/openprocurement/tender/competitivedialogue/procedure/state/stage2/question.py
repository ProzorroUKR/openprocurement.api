from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDEUStage2TenderDetailsState,
    CDUAStage2TenderDetailsState,
)
from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin


class CDStage2TenderQuestionStateMixin(TenderQuestionStateMixin):
    question_operation_allowed_tender_statuses = ("active.tendering",)
    question_shortlisted_firms_author_check = True


class CDEUStage2TenderQuestionState(CDStage2TenderQuestionStateMixin, CDEUStage2TenderDetailsState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)


class CDUAStage2TenderQuestionState(CDStage2TenderQuestionStateMixin, CDUAStage2TenderDetailsState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
