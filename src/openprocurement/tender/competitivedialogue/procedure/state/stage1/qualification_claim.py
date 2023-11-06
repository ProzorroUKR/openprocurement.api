from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import CDStage1TenderState
from openprocurement.tender.core.procedure.state.qualification_claim import QualificationClaimStateMixin


class CDStage1QualificationClaimState(QualificationClaimStateMixin, CDStage1TenderState):
    pass
