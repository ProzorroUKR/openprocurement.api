from openprocurement.tender.core.procedure.state.cancellation_complaint import (
    CancellationComplaintStateMixin,
)
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    COTenderState,
    DefenseTenderState,
    SimpleDefenseTenderState,
)


class AboveThresholdCancellationComplaintState(CancellationComplaintStateMixin, AboveThresholdTenderState):
    pass


class AboveThresholdUACancellationComplaintState(CancellationComplaintStateMixin, AboveThresholdUATenderState):
    pass


class AboveThresholdEUCancellationComplaintState(CancellationComplaintStateMixin, AboveThresholdEUTenderState):
    pass


class DefenseCancellationComplaintState(CancellationComplaintStateMixin, DefenseTenderState):
    pass


class SimpleDefenseCancellationComplaintState(CancellationComplaintStateMixin, SimpleDefenseTenderState):
    pass


class COCancellationComplaintState(CancellationComplaintStateMixin, COTenderState):
    pass
