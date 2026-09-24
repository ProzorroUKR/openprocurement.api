from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.criterion_rg import (
    RequirementGroupStateMixin,
)


class ARMARequirementGroupState(RequirementGroupStateMixin, ARMATenderState):
    pass
