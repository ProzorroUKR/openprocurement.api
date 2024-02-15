from openprocurement.tender.core.procedure.state.qualification_claim import (
    QualificationClaimStateMixin,
)
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


class ESCOQualificationClaimState(QualificationClaimStateMixin, ESCOTenderState):
    pass
