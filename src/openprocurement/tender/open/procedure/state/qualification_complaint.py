from openprocurement.tender.core.procedure.state.qualification_complaint import (
    QualificationComplaintStateMixin,
)
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    OpenTenderingTenderState,
)


class AboveThresholdEUQualificationComplaintState(QualificationComplaintStateMixin, AboveThresholdEUTenderState):
    pass


class OpenTenderingQualificationComplaintState(QualificationComplaintStateMixin, OpenTenderingTenderState):
    pass
