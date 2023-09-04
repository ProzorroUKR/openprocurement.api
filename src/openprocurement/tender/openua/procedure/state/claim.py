from openprocurement.tender.core.procedure.state.claim import ClaimState
from openprocurement.tender.openua.constants import CLAIM_SUBMIT_TIME


class OpenUAClaimState(ClaimState):
    tender_claim_submit_time = CLAIM_SUBMIT_TIME
