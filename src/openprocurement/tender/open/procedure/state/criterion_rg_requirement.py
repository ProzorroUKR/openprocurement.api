from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenRequirementState(RequirementStateMixin, OpenTenderState):
    pass
