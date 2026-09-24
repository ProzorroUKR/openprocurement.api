from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixin,
)
from openprocurement.tender.open.procedure.state.tender import OpenTenderState


class OpenCancellationStateMixin(CancellationStateMixin):
    _after_release_reason_types = [
        "noDemand",
        "unFixable",
        "forceMajeure",
        "expensesCut",
        "noOffer",
    ]
    cancellation_unsuccessful_items_check = True


class OpenCancellationState(OpenCancellationStateMixin, OpenTenderState):
    pass
