from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.openua.constants import CLAIM_SUBMIT_TIME
from openprocurement.tender.openua.procedure.state.tender import OpenUATenderState


class OpenUATenderClaimState(ClaimStateMixin, OpenUATenderState):
    tender_claim_submit_time = CLAIM_SUBMIT_TIME
