from openprocurement.tender.esco.procedure.state.tender import ESCOTenderStateMixin
from openprocurement.tender.core.procedure.state.claim import ClaimState


class ESCOClaimStateMixin(ESCOTenderStateMixin):
    pass


class ESCOClaimState(ESCOClaimStateMixin, ClaimState):
    pass
