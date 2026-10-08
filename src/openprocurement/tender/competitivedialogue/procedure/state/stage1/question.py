from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1EUTenderDetailsState,
    CDStage1UATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin


class CDStage1EUTenderQuestionState(TenderQuestionStateMixin, CDStage1EUTenderDetailsState):
    pass


class CDStage1UATenderQuestionState(TenderQuestionStateMixin, CDStage1UATenderDetailsState):
    pass
