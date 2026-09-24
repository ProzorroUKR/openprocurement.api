from openprocurement.tender.core.procedure.state.criterion_rg_requirement import (
    RequirementStateMixin,
)
from openprocurement.tender.core.procedure.state.tender import TenderState


class LimitedRequirementState(RequirementStateMixin, TenderState):
    pass
