from openprocurement.tender.cfaua.procedure.state.tender import CFAUATenderState
from openprocurement.tender.core.procedure.state.qualification_claim import (
    QualificationClaimStateMixin,
)


class CFAUAQualificationClaimState(QualificationClaimStateMixin, CFAUATenderState):
    pass
