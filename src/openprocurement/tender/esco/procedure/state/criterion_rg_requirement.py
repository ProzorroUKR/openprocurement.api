from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderTenderState


class ESCORequirementState(RequirementStateMixin, ESCOTenderTenderState):
    pass
