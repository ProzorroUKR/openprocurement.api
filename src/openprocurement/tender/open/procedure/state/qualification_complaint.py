from openprocurement.tender.core.procedure.state.qualification_complaint import (
    QualificationComplaintStateMixin,
)
from openprocurement.tender.open.procedure.state.tender import AboveThresholdEUTenderState


class AboveThresholdEUQualificationComplaintState(QualificationComplaintStateMixin, AboveThresholdEUTenderState):
    pass
