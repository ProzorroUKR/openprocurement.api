from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import Stage1EUTenderState


class CDRequirementGroupState(RequirementGroupStateMixin, Stage1EUTenderState):
    pass
