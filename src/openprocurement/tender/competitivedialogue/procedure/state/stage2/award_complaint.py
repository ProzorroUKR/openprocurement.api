from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDUAStage2TenderState,
    CDEUStage2TenderState,
)
from openprocurement.tender.core.procedure.state.award_complaint import AwardComplaintStateMixin


class CDUAStage2AwardComplaintState(AwardComplaintStateMixin, CDUAStage2TenderState):
    pass


class CDEUStage2AwardComplaintState(AwardComplaintStateMixin, CDEUStage2TenderState):
    pass
