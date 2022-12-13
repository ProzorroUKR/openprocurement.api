from openprocurement.tender.belowthreshold.procedure.state.criterion import BelowThresholdCriterionStateMixin
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState


class CFASelectionCriterionState(BelowThresholdCriterionStateMixin, CFASelectionTenderState):
    pass
