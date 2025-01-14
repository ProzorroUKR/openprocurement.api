from openprocurement.tender.belowthreshold.procedure.state.cancellation import (
    BelowThresholdCancellationStateMixing,
)
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)


class PQCancellationStateMixing(BelowThresholdCancellationStateMixing):
    _after_release_reason_types = [
        "noDemand",
        "unFixable",
        "forceMajeure",
        "expensesCut",
    ]


class PQCancellationState(PQCancellationStateMixing, PriceQuotationTenderState):
    pass
