from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import CDStage1TenderState


class CDRequirementState(RequirementStateMixin, CDStage1TenderState):
    pass
