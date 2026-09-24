from openprocurement.tender.belowthreshold.procedure.state.tender import (
    BelowThresholdTenderState,
)
from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixin,
)


class BelowThresholdCancellationStateMixin(CancellationStateMixin):
    _before_release_reason_types = None
    _after_release_reason_types = ["noDemand", "unFixable", "expensesCut"]
    cancellation_complaint_period_check = False


class BelowThresholdCancellationState(BelowThresholdCancellationStateMixin, BelowThresholdTenderState):
    pass
