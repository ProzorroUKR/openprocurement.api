from openprocurement.tender.competitivedialogue.constants import CD_CLAIM_SUBMIT_TIME
from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import (
    CDStage1TenderState,
)
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin


class CDStage1TenderClaimState(ClaimStateMixin, CDStage1TenderState):
    tender_claim_submit_time = CD_CLAIM_SUBMIT_TIME
