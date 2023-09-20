from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import CDStage1TenderState


class CDRequirementGroupState(RequirementGroupStateMixin, CDStage1TenderState):
    pass
