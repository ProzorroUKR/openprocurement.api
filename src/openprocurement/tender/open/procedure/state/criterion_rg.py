from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenRequirementGroupState(RequirementGroupStateMixin, OpenTenderState):
    pass
