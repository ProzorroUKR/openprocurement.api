from openprocurement.tender.competitiveordering.procedure.state.tender import (
    COTenderState,
)
from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixing,
)


class COCancellationStateMixing(CancellationStateMixing):
    _after_release_reason_types = [
        "noDemand",
        "unFixable",
        "forceMajeure",
        "expensesCut",
        "noOffer",
    ]
    cancellation_unsuccessful_items_check = True


class COCancellationState(COCancellationStateMixing, COTenderState):
    pass
