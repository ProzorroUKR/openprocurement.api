from openprocurement.tender.cfaua.constants import CLAIM_SUBMIT_TIME
from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin


class CFAUATenderClaimState(ClaimStateMixin, CFAUATenderState):
    tender_claim_submit_time = CLAIM_SUBMIT_TIME
