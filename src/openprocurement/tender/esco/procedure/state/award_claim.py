from openprocurement.tender.esco.procedure.state.claim import ESCOClaimStateMixin
from openprocurement.tender.core.procedure.state.award_claim import AwardClaimState


class ESCOAwardClaimState(ESCOClaimStateMixin, AwardClaimState):
    pass
