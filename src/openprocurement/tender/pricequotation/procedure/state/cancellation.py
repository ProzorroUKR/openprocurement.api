from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixing
from openprocurement.tender.pricequotation.procedure.state.tender import (
    PriceQuotationTenderState,
)


class PQCancellationStateMixing(CancellationStateMixing):
    _before_release_reason_types = None
    cancellation_complaint_period_check = False
    _after_release_reason_types = [
        "noDemand",
        "unFixable",
        "forceMajeure",
        "expensesCut",
    ]
    procurement_kinds_not_required_sign = ("other",)


class PQCancellationState(PQCancellationStateMixing, PriceQuotationTenderState):
    pass
