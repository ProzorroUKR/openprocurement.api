from openprocurement.tender.core.procedure.state.cancellation import (
    CancellationStateMixing,
)
from openprocurement.tender.requestforproposal.procedure.state.tender import (
    RequestForProposalTenderState,
)


class RequestForProposalCancellationStateMixing(CancellationStateMixing):
    _before_release_reason_types = None
    _after_release_reason_types = ["noDemand", "unFixable", "expensesCut"]
    should_validate_cancellation_report_doc_required = False
    cancellation_complaint_period_check = False


class RequestForProposalCancellationState(RequestForProposalCancellationStateMixing, RequestForProposalTenderState):
    pass
