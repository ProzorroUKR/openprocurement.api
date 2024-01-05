from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixing
from openprocurement.tender.belowthreshold.procedure.state.tender import BelowThresholdTenderState


class BelowThresholdCancellationStateMixing(CancellationStateMixing):

    _before_release_reason_types = None
    _after_release_reason_types = ["noDemand", "unFixable", "expensesCut"]

    @staticmethod
    def validate_cancellation_in_complaint_period(request, tender, cancellation):
        pass


class BelowThresholdCancellationState(BelowThresholdCancellationStateMixing, BelowThresholdTenderState):
    pass
