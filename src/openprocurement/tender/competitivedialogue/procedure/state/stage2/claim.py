from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDUAStage2TenderState,
    CDEUStage2TenderState,
)
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.openua.constants import CLAIM_SUBMIT_TIME


class CDUAStage2TenderClaimState(ClaimStateMixin, CDUAStage2TenderState):
    tender_claim_submit_time = CLAIM_SUBMIT_TIME


class CDEUStage2TenderClaimState(ClaimStateMixin, CDEUStage2TenderState):
    tender_claim_submit_time = CLAIM_SUBMIT_TIME
