from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixing,
)
from openprocurement.tender.limited.procedure.state.tender import NegotiationTenderState


class ReportingCancellationStateMixing(CancellationStateMixing):
    cancellation_complaint_period_check = False
    _before_release_reason_types = ["cancelled", "unsuccessful"]
    _after_release_reason_types = [
        "noDemand",
        "unFixable",
        "forceMajeure",
        "expensesCut",
    ]


class ReportingCancellationState(ReportingCancellationStateMixing, NegotiationTenderState):
    pass


class NegotiationCancellationStateMixing(CancellationStateMixing):
    _before_release_reason_types = ["cancelled", "unsuccessful"]
    _after_release_reason_types = [
        "noObjectiveness",
        "unFixable",
        "noDemand",
        "expensesCut",
        "dateViolation",
    ]
    cancellation_complete_lots_check = True
    cancellation_deprecated_activation_without_active_award = True


class NegotiationCancellationState(NegotiationCancellationStateMixing, NegotiationTenderState):
    pass
