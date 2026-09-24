from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.openeu.constants import CLAIM_SUBMIT_TIME
from openprocurement.tender.openeu.procedure.state.tender import OpenEUTenderState


class OpenEUTenderClaimState(ClaimStateMixin, OpenEUTenderState):
    tender_claim_submit_time = CLAIM_SUBMIT_TIME
