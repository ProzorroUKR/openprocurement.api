from openprocurement.tender.cfaselectionua.procedure.state.tender import (
    CFASelectionTenderState,
)
from openprocurement.tender.core.procedure.state.cancellation import CancellationStateMixin


class CFASelectionCancellationState(CancellationStateMixin, CFASelectionTenderState):
    cancellation_complaint_period_check = False
    _before_release_reason_types = None
    all_documents_should_be_public = True
