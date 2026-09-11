from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixing,
)
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenUACancellationStateMixing(CancellationStateMixing):
    _after_release_reason_types = [
        "noDemand",
        "unFixable",
        "forceMajeure",
        "expensesCut",
        "noOffer",
    ]
    cancellation_unsuccessful_items_check = True


class OpenCancellationState(OpenUACancellationStateMixing, OpenTenderState):
    pass
