from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.openua.constants import CLAIM_SUBMIT_TIME


class CFAUATenderClaimState(ClaimStateMixin, CFAUATenderState):
    tender_claim_submit_time = CLAIM_SUBMIT_TIME
