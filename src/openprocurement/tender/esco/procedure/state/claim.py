from openprocurement.tender.esco.procedure.state.tender import ESCOTenderState
from openprocurement.tender.core.procedure.state.claim import ClaimStateMixin


class ESCOClaimState(ClaimStateMixin, ESCOTenderState):
    pass
