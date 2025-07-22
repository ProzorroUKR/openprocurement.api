from openprocurement.tender.competitiveordering.procedure.state.tender import (
    COTenderState,
)
from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState


class COTenderComplaintState(TenderComplaintState, COTenderState):
    should_validate_complaint_author_qualified_supplier = True
