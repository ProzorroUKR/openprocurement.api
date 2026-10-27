from openprocurement.tender.core.procedure.state.qualification_claim import (
    QualificationClaimStateMixin,
)
from openprocurement.tender.open.procedure.state.tender import (
    AboveThresholdEUTenderState,
    OpenTenderingTenderState,
)


class AboveThresholdEUQualificationClaimState(QualificationClaimStateMixin, AboveThresholdEUTenderState):
    pass


class OpenTenderingQualificationClaimState(QualificationClaimStateMixin, OpenTenderingTenderState):
    pass
