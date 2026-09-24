from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender_details import (
    CDStage1TenderDetailsStateMixin,
)
from openprocurement.tender.core.procedure.state.question import TenderQuestionStateMixin


class CDStage1TenderQuestionState(TenderQuestionStateMixin, CDStage1TenderDetailsStateMixin):
    pass
