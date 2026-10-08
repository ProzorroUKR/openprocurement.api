from openprocurement.api.auth import AccreditationLevel
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender_details import (
    CDStage2EUTenderDetailsState,
    CDStage2UATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin


class CDStage2TenderQuestionStateMixin(TenderQuestionStateMixin):
    question_create_accreditations = None

    question_shortlisted_firms_author_check = True


class CDStage2EUTenderQuestionState(CDStage2TenderQuestionStateMixin, CDStage2EUTenderDetailsState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)


class CDStage2UATenderQuestionState(CDStage2TenderQuestionStateMixin, CDStage2UATenderDetailsState):
    question_create_accreditations = (AccreditationLevel.ACCR_4,)
