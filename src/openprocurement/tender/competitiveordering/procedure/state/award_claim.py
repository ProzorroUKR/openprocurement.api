from openprocurement.tender.competitiveordering.procedure.state.tender import (
    COTenderState,
)
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin


class COAwardClaimState(AwardClaimStateMixin, COTenderState):
    pass
