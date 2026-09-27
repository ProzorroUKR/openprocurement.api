from openprocurement.tender.arma.procedure.state.tender_details import (
    ARMATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg_requirement import RequirementStateMixin


class ARMARequirementState(RequirementStateMixin, ARMATenderDetailsState):
    pass
