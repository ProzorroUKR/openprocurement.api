from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixin
from openprocurement.tender.openuadefense.procedure.state.tender import (
    DefenseTenderState,
)


class DefenseCancellationStateMixin(CancellationStateMixin):
    cancellation_unsuccessful_items_check = True
    _after_release_reason_types = ["noDemand", "unFixable", "expensesCut"]


class DefenseCancellationState(DefenseCancellationStateMixin, DefenseTenderState):
    pass
