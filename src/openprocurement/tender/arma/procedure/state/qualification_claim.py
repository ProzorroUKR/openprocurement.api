from openprocurement.tender.arma.procedure.state.tender import TenderState
from openprocurement.tender.core.procedure.state.qualification_claim import (
    QualificationClaimStateMixin,
)


class QualificationClaimState(QualificationClaimStateMixin, TenderState):
    pass
