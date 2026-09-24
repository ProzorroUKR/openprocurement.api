from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)
from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixing


class CFASelectionCancellationState(CancellationStateMixing, CFASelectionTenderState):
    cancellation_complaint_period_check = False
    _before_release_reason_types = None
    _after_release_reason_types = [
        "noDemand",
        "unFixable",
        "forceMajeure",
        "expensesCut",
    ]
    all_documents_should_be_public = True
