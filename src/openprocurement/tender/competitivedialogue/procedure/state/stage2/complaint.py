from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDEUStage2TenderState,
    CDUAStage2TenderState,
)
from openprocurement.tender.core.procedure.state.complaint import TenderComplaintState


class CDUAStage2TenderComplaintState(TenderComplaintState, CDUAStage2TenderState):
    pass


class CDEUStage2TenderComplaintState(TenderComplaintState, CDEUStage2TenderState):
    pass
