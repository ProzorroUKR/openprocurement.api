from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.openeu.procedure.state.tender import BaseOpenEUTenderState
from openprocurement.tender.openua.constants import CLAIM_SUBMIT_TIME


class OpenEUTenderClaimState(ClaimStateMixin, BaseOpenEUTenderState):
    tender_claim_submit_time = CLAIM_SUBMIT_TIME
