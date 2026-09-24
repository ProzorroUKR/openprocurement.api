from openprocurement.tender.arma.constants import CLAIM_SUBMIT_TIME
from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin


class ARMAClaimState(ClaimStateMixin, ARMATenderState):
    tender_claim_submit_time = CLAIM_SUBMIT_TIME
