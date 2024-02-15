from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import (
    CDStage1TenderState,
)
from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin


class CDCriterionState(CriterionStateMixin, CDStage1TenderState):
    pass
