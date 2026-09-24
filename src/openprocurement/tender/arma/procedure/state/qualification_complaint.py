from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.qualification_complaint import (
    QualificationComplaintStateMixin,
)


class ARMAQualificationComplaintState(QualificationComplaintStateMixin, ARMATenderState):
    pass
