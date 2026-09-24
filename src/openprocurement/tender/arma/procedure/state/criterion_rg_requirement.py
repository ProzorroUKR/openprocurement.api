from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import (
    RequirementStateMixin,
)


class ARMARequirementState(RequirementStateMixin, ARMATenderState):
    pass
