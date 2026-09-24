from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixin,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RFPTenderState,
)


class RFPCancellationStateMixin(CancellationStateMixin):
    _before_release_reason_types = None
    _after_release_reason_types = ["noDemand", "unFixable", "expensesCut"]
    cancellation_report_doc_required_check = False
    cancellation_complaint_period_check = False


class RFPCancellationState(RFPCancellationStateMixin, RFPTenderState):
    pass
