from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState


class CFAUARequirementState(RequirementStateMixin, CFASelectionTenderState):
    pass
