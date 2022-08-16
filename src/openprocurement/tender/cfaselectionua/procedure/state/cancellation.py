from openprocurement.tender.belowthreshold.procedure.state.cancellation import BelowThresholdCancellationStateMixing
from openprocurement.tender.cfaselectionua.procedure.state.tender import CFASelectionTenderState


class CFASelectionCancellationState(BelowThresholdCancellationStateMixing, CFASelectionTenderState):
    _before_release_reason_types = None
    _after_release_reason_types = ["noDemand", "unFixable", "forceMajeure", "expensesCut"]
    _after_release_statuses = ["draft", "unsuccessful", "active"]
