from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixin,
)
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState


class ReportingCancellationStateMixin(CancellationStateMixin):
    cancellation_complaint_period_check = False


class ReportingCancellationState(ReportingCancellationStateMixin, NegotiationTenderState):
    pass


class NegotiationCancellationStateMixin(CancellationStateMixin):
    _after_release_reason_types = [
        "noObjectiveness",
        "unFixable",
        "noDemand",
        "expensesCut",
        "dateViolation",
    ]
    cancellation_complete_lots_check = True
    cancellation_deprecated_activation_without_active_award = True


class NegotiationCancellationState(NegotiationCancellationStateMixin, NegotiationTenderState):
    pass
