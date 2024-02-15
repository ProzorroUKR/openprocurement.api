from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDEUStage2TenderState,
)
from openprocurement.tender.core.procedure.state.qualification_complaint import (
    QualificationComplaintStateMixin,
)


class CDEUStage2QualificationComplaintState(QualificationComplaintStateMixin, CDEUStage2TenderState):
    pass
