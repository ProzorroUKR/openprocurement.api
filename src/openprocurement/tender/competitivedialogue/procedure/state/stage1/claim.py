from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import (
    CDStage1TenderState,
)
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.openua.constants import CLAIM_SUBMIT_TIME


class CDStage1TenderClaimState(ClaimStateMixin, CDStage1TenderState):
    tender_claim_submit_time = CLAIM_SUBMIT_TIME
