from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUARequirementState(RequirementStateMixin, OpenUATenderState):
    pass
