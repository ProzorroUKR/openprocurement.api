from openprocurement.tender.arma.procedure.state.tender_details import (
    ARMATenderDetailsState,
)
from openprocurement.tender.core.procedure.state.criterion_rg import RequirementGroupStateMixin


class ARMARequirementGroupState(RequirementGroupStateMixin, ARMATenderDetailsState):
    pass
