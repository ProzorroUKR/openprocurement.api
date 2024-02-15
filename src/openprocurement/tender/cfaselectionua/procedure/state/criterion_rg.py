from openprocurement.tender.belowthreshold.procedure.state.criterion_rg import (
    BelowThresholdRequirementGroupStateMixin,
)
from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)


class CFASelectionRequirementGroupState(BelowThresholdRequirementGroupStateMixin, CFASelectionTenderState):
    pass
