from openprocurement.tender.arma.procedure.state.tender import ARMATenderState
from openprocurement.tender.core.procedure.state.qualification_claim import (
    QualificationClaimStateMixin,
)


class ARMAQualificationClaimState(QualificationClaimStateMixin, ARMATenderState):
    pass
