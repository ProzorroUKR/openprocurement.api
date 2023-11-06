from openprocurement.tender.competitivedialogue.procedure.state.stage1.tender import CDStage1TenderState
from openprocurement.tender.core.procedure.state.qualification_complaint import QualificationComplaintStateMixin


class CDStage1QualificationComplaintState(QualificationComplaintStateMixin, CDStage1TenderState):
    pass
