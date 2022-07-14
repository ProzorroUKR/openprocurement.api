from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import Stage1TenderState


class CDRequirementState(RequirementStateMixin, Stage1TenderState):
    pass