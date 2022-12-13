from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUARequirementGroupState(RequirementGroupStateMixin, OpenUATenderState):
    pass
