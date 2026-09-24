from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDStage2EUTenderState,
)
from openprocurement.tender.core.procedure.state.qualification_complaint import (
    QualificationComplaintStateMixin,
)


class CDStage2EUQualificationComplaintState(QualificationComplaintStateMixin, CDStage2EUTenderState):
    pass
