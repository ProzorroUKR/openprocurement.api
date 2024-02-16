from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDEUStage2TenderState,
    CDUAStage2TenderState,
)
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimStateMixin


class CDUAStage2AwardClaimState(AwardClaimStateMixin, CDUAStage2TenderState):
    pass


class CDEUStage2AwardClaimState(AwardClaimStateMixin, CDEUStage2TenderState):
    pass
