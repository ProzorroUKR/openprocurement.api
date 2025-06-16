from openprocurement.tender.competitiveordering.procedure.state.tender import (
    COTenderState,
)
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin


class COTenderClaimState(ClaimStateMixin, COTenderState):
    pass
