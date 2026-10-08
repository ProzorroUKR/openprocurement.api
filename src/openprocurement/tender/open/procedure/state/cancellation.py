from openprocurement.tender.core.procedure.models.award import Award
from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixin,
)
from openprocurement.tender.core.procedure.state.tender import TenderState
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdTenderState,
    AboveThresholdUATenderState,
    BelowThresholdTenderState,
    COTenderState,
    DefenseTenderState,
    RFPTenderState,
)


class AboveThresholdCancellationStateMixin(CancellationStateMixin):
    _after_release_reason_types = [
        "noDemand",
        "unFixable",
        "forceMajeure",
        "expensesCut",
        "noOffer",
    ]
    cancellation_unsuccessful_items_check = True


class AboveThresholdCancellationState(AboveThresholdCancellationStateMixin, AboveThresholdTenderState):
    pass


class AboveThresholdUACancellationStateMixin(CancellationStateMixin):
    cancellation_unsuccessful_items_check = True


class AboveThresholdUACancellationState(AboveThresholdUACancellationStateMixin, AboveThresholdUATenderState):
    pass


class AboveThresholdEUCancellationStateMixin(CancellationStateMixin):
    cancellation_unsuccessful_items_check = True


class AboveThresholdEUCancellationState(AboveThresholdEUCancellationStateMixin, TenderState):
    award_class = Award


class DefenseCancellationStateMixin(CancellationStateMixin):
    cancellation_unsuccessful_items_check = True
    _after_release_reason_types = ["noDemand", "unFixable", "expensesCut"]


class DefenseCancellationState(DefenseCancellationStateMixin, DefenseTenderState):
    pass


class COCancellationStateMixin(CancellationStateMixin):
    _after_release_reason_types = [
        "noDemand",
        "unFixable",
        "forceMajeure",
        "expensesCut",
        "noOffer",
    ]
    cancellation_unsuccessful_items_check = True


class COCancellationState(COCancellationStateMixin, COTenderState):
    pass


class BelowThresholdCancellationStateMixin(CancellationStateMixin):
    _before_release_reason_types = None
    _after_release_reason_types = ["noDemand", "unFixable", "expensesCut"]
    cancellation_complaint_period_check = False


class BelowThresholdCancellationState(BelowThresholdCancellationStateMixin, BelowThresholdTenderState):
    pass


class RFPCancellationStateMixin(CancellationStateMixin):
    _before_release_reason_types = None
    _after_release_reason_types = ["noDemand", "unFixable", "expensesCut"]
    cancellation_report_doc_required_check = False
    cancellation_complaint_period_check = False


class RFPCancellationState(RFPCancellationStateMixin, RFPTenderState):
    pass
