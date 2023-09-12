from openprocurement.tender.esco.procedure.state.claim import ESCOClaimStateMixin
from openprocurement.tender.core.procedure.state.qualification_claim import QualificationClaimState


class ESCOQualificationClaimState(ESCOClaimStateMixin, QualificationClaimState):
    pass
