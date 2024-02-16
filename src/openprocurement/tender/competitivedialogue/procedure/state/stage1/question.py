from openprocurement.api.auth import ACCR_4
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1TenderDetailsState,
)
from openprocurement.tender.openua.procedure.state.question import (
    UATenderQuestionStateMixin,
)


class CDStage1TenderQuestionState(UATenderQuestionStateMixin, CDStage1TenderDetailsState):
    question_create_accreditations = (ACCR_4,)
