from openprocurement.tender.competitiveordering.procedure.state.tender import (
    COTenderState,
)
from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState


class COTenderComplaintState(TenderComplaintState, COTenderState):
    pass
