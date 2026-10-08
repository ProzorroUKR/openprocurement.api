from openprocurement.tender.competitivedialogue.procedure.state.stage2.tender import (
    CDStage2EUTenderState,
)
from openprocurement.tender.core.procedure.state.qualification_claim import (
    QualificationClaimStateMixin,
)


class CDStage2EUQualificationClaimState(QualificationClaimStateMixin, CDStage2EUTenderState):
    pass
