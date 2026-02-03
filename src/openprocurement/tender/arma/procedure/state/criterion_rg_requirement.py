from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import (
    RequirementStateMixin,
)


class RequirementState(RequirementStateMixin, TenderState):
    pass
