from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin
from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState


class ESCOClaimState(ClaimStateMixin, ESCOTenderState):
    pass
