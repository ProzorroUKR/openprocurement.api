from openprocurement.tender.core.procedure.state.criterion import CriterionStateMixin
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import CDStage1TenderState


class CDCriterionState(CriterionStateMixin, CDStage1TenderState):
    pass
