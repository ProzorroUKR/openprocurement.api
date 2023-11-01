from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import CDEUStage2TenderState
from openprocurement.tender.core.procedure.state.qualification_claim import QualificationClaimStateMixin


class CDEUStage2QualificationClaimState(QualificationClaimStateMixin, CDEUStage2TenderState):
    pass
