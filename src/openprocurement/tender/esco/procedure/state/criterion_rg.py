from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


class ESCORequirementGroupState(RequirementGroupStateMixin, ESCOTenderState):
    pass
