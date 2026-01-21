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
    procurement_kinds_not_required_sign = ("other",)


class PQCancellationState(PQCancellationStateMixing, PriceQuotationTenderState):
    pass
