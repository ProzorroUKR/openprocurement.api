from openprocurement.tender.competitivedialogue.constants import CLAIM_SUBMIT_TIME
from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDStage2EUTenderState,
    CDStage2UATenderState,
)
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin


class CDStage2UATenderClaimState(ClaimStateMixin, CDStage2UATenderState):
    tender_claim_submit_time = CLAIM_SUBMIT_TIME


class CDStage2EUTenderClaimState(ClaimStateMixin, CDStage2EUTenderState):
    tender_claim_submit_time = CLAIM_SUBMIT_TIME
