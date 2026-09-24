from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixing
from openprocurement.tender.openuadefense.procedure.state.tender import (
    OpenUADefenseTenderState,
)


class UADefenseCancellationStateMixing(CancellationStateMixing):
    cancellation_unsuccessful_items_check = True
    _after_release_reason_types = ["noDemand", "unFixable", "expensesCut"]


class UADefenseCancellationState(UADefenseCancellationStateMixing, OpenUADefenseTenderState):
    pass
