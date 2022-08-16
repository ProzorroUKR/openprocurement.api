from openprocurement.tender.openua.procedure.state.cancellation import OpenUACancellationStateMixing
from openprocurement.tender.openuadefense.procedure.state.tender import OpenUADefenseTenderState


class UADefenseCancellationStateMixing(OpenUACancellationStateMixing):
    _after_release_reason_types = ["noDemand", "unFixable", "expensesCut"]


class UADefenseCancellationState(UADefenseCancellationStateMixing, OpenUADefenseTenderState):
    pass
