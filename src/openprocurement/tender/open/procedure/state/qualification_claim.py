from openprocurement.tender.core.procedure.state.qualification_claim import (
    QualificationClaimStateMixin,
)
from openprocurement.tender.open.procedure.state.tender import AboveThresholdEUTenderState


class AboveThresholdEUQualificationClaimState(QualificationClaimStateMixin, AboveThresholdEUTenderState):
    pass
